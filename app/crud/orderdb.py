from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.models.order import Order
from app.repositories.models.order_item import OrderItem
from app.repositories.models.stock_batch import StockBatch
from sqlalchemy import update, select, asc # asc - по возрастанию (первые - самые старые партии)
from datetime import timezone


async def create_order_with_items(session: AsyncSession, dto):
    stmt_check = select(Order).where(Order.posting_number == dto.posting_number)
    res_check = await session.execute(stmt_check)
    existing_order = res_check.scalar_one_or_none()

    if existing_order:
        return  # Если заказ уже есть в базе, просто выходим. Для Озона это будет успех (200 OK)

    order = Order(
        posting_number=dto.posting_number,
        status="posting_created",
    )

    session.add(order)

    for item_dto in dto.products:
        qty_to_deduct = item_dto.quantity # счетчик списания с партий
        stmt_batches = select(StockBatch).where(StockBatch.sku == item_dto.sku, StockBatch.current_quantity > 0).order_by(asc(StockBatch.created_at))
        res = await session.execute(stmt_batches)
        batches = res.scalars().all()

        for batch in batches:
            # Определяем, сколько штук мы можем забрать из ТЕКУЩЕЙ партии
            allocated_qty = min(batch.current_quantity, qty_to_deduct)
            # Списываем из партии
            batch.current_quantity -= allocated_qty
            qty_to_deduct -= allocated_qty

            # Создаем OrderItem именно для этой части товара с его реальной себестоимостью!
            order_item = OrderItem(
                posting_number=dto.posting_number,
                sku=item_dto.sku,
                quantity=allocated_qty,  # Фиксируем сколько взяли из этой партии
                price=item_dto.price,
                commission_amount=item_dto.commission_amount,
                payout=item_dto.payout,
                purchase_price=batch.purchase_price  # себестоимость
            )
            session.add(order_item)

            if qty_to_deduct <= 0:
                break

        # Защита от оверселла: если после всех партий товар еще нужно списать
        # Здесь надо сделать уведомление, что сотрудник забыл партию внести
        # if qty_to_deduct > 0:
        #    overdue_batch = StockBatch(
        #        sku=item_dto.sku,
        #        purchase_price=0.0,                # 0 рублей, чтобы временно не ломать маржу
        #        initial_quantity=0,             # Партия создана виртуально
        #        current_quantity=-qty_to_deduct  # Уводим остаток в минус
        #    )
        #   session.add(overdue_batch)


    await session.commit()

async def update_order_status(session: AsyncSession, dto):
    # 1. Сначала находим заказ в базе данных
    stmt = select(Order).where(Order.posting_number == dto.posting_number)
    res = await session.execute(stmt)
    order = res.scalar_one_or_none()

    if order:
        # ПОДСТРАХОВКА: Если у даты из вебхука почему-то нет таймзоны,
        # принудительно задаем ей UTC перед сравнением с базой
        webhook_date = dto.changed_state_date
        if webhook_date.tzinfo is None:
            webhook_date = webhook_date.replace(tzinfo=timezone.utc)
        # Сравниваем дату из вебхука с нашей updated_at
        # Если Озон прислал старое событие, которое случилось до нашего updated_at — игнорируем
        if webhook_date< order.updated_at:
            return  # Выходим из функции, ничего не перезаписывая

        # Если вебхук свежий — обновляем статус
        order.status = dto.new_state.value
        # Поле updated_at обновится автоматически благодаря onupdate=lambda: datetime.now(timezone.utc)

        await session.commit()

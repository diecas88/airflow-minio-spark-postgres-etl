--paises con mas ordenes
select c.country, count(o.id) orders from public.orders o
left join public.customers c on o.customer_id = c.id 
group by c.country 
order by count(o.id) desc;

-- ventas de categorias por año, ordenadas por año y ventas
select extract(year from date(o.order_date)) as year ,p.category,count(o.id) as quantity,sum(cast(p.price as decimal)*o.quantity_product) sales  from public.orders o
inner join public.products p
on o.product_id = cast(p.id as int)
group by p.category,extract(year from date(o.order_date))
order by extract(year from date(o.order_date)),sum(cast(p.price as decimal)*o.quantity_product) desc

-- ventas por medio de pago
select extract(year from date(o.order_date)) as year ,
o.cash_or_card,
sum(cast(p.price as decimal)*o.quantity_product) sales
from public.orders o
inner join public.products p
on o.product_id = cast(p.id as int)
group by extract(year from date(o.order_date)),o.cash_or_card
order by extract(year from date(o.order_date)) desc,sum(cast(p.price as decimal)*o.quantity_product) desc
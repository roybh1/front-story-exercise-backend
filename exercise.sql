select day_only, id, name, sum(revenue), sum(cost), sum(profit), sum(roi), avg(uv), avg(cpc) from (

select cost.data_date as dt, cost.campaign_id as id , cost.campaign_name as name, cost.clicks as clicks , cost.cost as cost, rev.revenue as revenue
uv as uv, cpc as cpc, uv/cpc as roi, revenue - cost as profit, date(cost.data_date) as day_only from (

SELECT cost.data_date as dt, cost.campaign_id as id , cost.campaign_name as name, cost.clicks as clicks , cost.cost as cost, rev.revenue as revenue
revenue/click as uv, cost/clicks as cpc
from cost as cost
inner join revenue as rev
ON cost.campaign_id = revenue.campaign_id

)
)
group by day_only, id
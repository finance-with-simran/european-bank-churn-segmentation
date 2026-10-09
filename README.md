# Customer Segmentation & Churn Pattern Analytics in European Banking

An interactive Streamlit dashboard exploring customer churn patterns in a European banking dataset. The project compares churn rates and customer counts across geography, age, tenure, product count, and activity.

## Live dashboard

[Open the live dashboard]:https://finance-with-simran-european-bank-churn-segmentation-app-ahbwvy.streamlit.app/

## Project objective

Explore which customer segments have higher observed churn rates and describe the account balance associated with customers marked as churned. This is **descriptive analysis**: it does not establish the causes of churn or predict which individual customers will leave.

## Key findings

- The dataset contains **10,000 customers**: **2,037 churned** and **7,963 retained**. Overall churn rate: **20.37%**.
- **Germany** had the highest geographic churn rate: **32.44%** (814 of 2,509 customers), accounting for about **40% of all churn cases**.
- Customers aged **50–59** had the highest churn rate in each country: Germany **70.04%**, France **51.57%**, and Spain **45.71%**.
- Churn was **26.85%** among inactive customers and **14.27%** among active customers.
- Churn rates were high among customers with three products (**82.71%**) and four products (**100%**). The four-product group has only **60 customers**, so its rate should be interpreted cautiously.
- Churned customers held **185,588,094.63** in recorded account balance—**24.26%** of the dataset’s total recorded balance. The dataset does not specify the currency. These figures are **not** identified as euros, revenue, or financial loss.

## Dashboard features

- Interactive filters for customer segments
- Portfolio KPIs and churn-rate comparisons
- Customer counts shown alongside segment rates
- Recorded balance context for churned customers
- Filtered-data download
- Metric definitions, limitations, and suggested next steps

## Repository files

Place these files in the repository root:

- `app.py` — Streamlit dashboard
- `European_Bank.csv` — dataset used by the dashboard
- `requirements.txt` — Python dependencies
- `README.md` — project information

## Deploy with Streamlit Community Cloud

1. Push the project files to a GitHub repository.
2. Open Streamlit Community Cloud and select **Create app**.
3. Choose this repository and its deployment branch.
4. Set the app file path to `app.py`.
5. Deploy the app, then replace the live-dashboard placeholder above with the URL Streamlit provides.

The dataset filename must be exactly `European_Bank.csv` and the file must be included in the repository.

## Methods and limitations

Churn rate is calculated as customers with `Exited = 1` divided by the number of customers in the relevant group. Segment comparisons describe patterns in the supplied records; they do not demonstrate that a customer characteristic causes churn.

The dataset’s currency, time period, sampling method, and business definitions are not confirmed here. Balance amounts should be treated as recorded dataset currency units—not as revenue, profit, or financial loss. Rates for small groups may be unstable.

## Suggested next steps

- Validate high-rate segments and their sample sizes with business stakeholders.
- Investigate customer feedback, service experience, pricing, and product fit before proposing interventions.
- Test retention ideas using a comparison group and measure incremental retention and cost.
- Confirm currency and time coverage before presenting balances as financial KPIs.

## Technology

Python · Streamlit · pandas · Plotly

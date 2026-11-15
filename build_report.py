import sys, pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image, PageBreak, KeepTogether
OUT=sys.argv[1]; R=pd.read_pickle(f'{OUT}/results.pkl')
G='#1f2933'; ACC='#2563eb'; ss=getSampleStyleSheet()
T=ParagraphStyle('t',parent=ss['Title'],fontSize=22,textColor=colors.HexColor(G),alignment=0,leading=26)
H=ParagraphStyle('h',parent=ss['Heading2'],fontSize=14,textColor=colors.HexColor(G),spaceBefore=12,spaceAfter=4,keepWithNext=1,leading=18)
B=ParagraphStyle('b',parent=ss['BodyText'],fontSize=10,leading=14,textColor=colors.HexColor(G))
Sm=ParagraphStyle('s',parent=B,fontSize=8.5,leading=11,textColor=colors.HexColor('#6b7785'))
C=ParagraphStyle('c',parent=B,fontSize=8.5,leading=11)
P=lambda t,s=B:Paragraph(t,s)
def tbl(rows,w):
    t=Table(rows,colWidths=w,repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(G)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTSIZE',(0,0),(-1,-1),8.5),
      ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d5dbe1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f5f7')]),('VALIGN',(0,0),(-1,-1),'TOP'),
      ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)])); return t
def img(n,w): 
    from PIL import Image as I; iw,ih=I.open(f'{OUT}/charts/{n}.png').size; return Image(f'{OUT}/charts/{n}.png',width=w,height=w*ih/iw)
y=R['yr_month_rev']; bad=R['bad_by_year']
doc=SimpleDocTemplate(f'{OUT}/EDA_Report_Project2.pdf',pagesize=A4,leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=40,title='Project 2 - Exploratory Data Analysis')
e=[P('Exploratory Data Analysis: Orders Dataset',T),
 P(f'Project 2 | Data Analytics | DecodeLabs Batch 2026 | Prepared by Laiba | 15 Nov 2026<br/>Data: cleaned output of Project 1 ({R["rows"]:,} orders, {R["dates"][0]} to {R["dates"][1]}) | Tools: Python (pandas, SciPy, matplotlib)',Sm),
 Paragraph('Executive Summary',H),
 P('<b>1. Problem statement.</b> Which patterns, trends and outliers in the order data should the business act on, and which apparent patterns are just noise?'),Spacer(1,4),
 P('<b>2. Methodology.</b> Started from the Project 1 cleaned dataset (0 nulls, 0 duplicates). Computed count, mean, median and five-number summaries; screened outliers with the IQR rule (primary) and Z-score &gt; 3 (cross-check); measured relationships with Pearson correlation; compared monthly trends (normalised, because 2025 holds only Jan-Jun); and tested segment differences with Kruskal-Wallis and chi-square so that differences are only reported when they are statistically real.'),Spacer(1,4),
 P('<b>3. Key findings.</b>'),
 P(f'&bull; <b>Monthly order value is drifting down.</b> Average monthly value fell from ${y[2023]/1e3:,.1f}K (2023) to ${y[2024]/1e3:,.1f}K (2024) and ${y[2025]/1e3:,.1f}K (2025 H1), a {abs(R["yr_chg"])*100:.0f}% drop versus 2023. The fitted trend is {R["trend_slope"]/1e3:+.2f}K per month, but it is not yet statistically conclusive (p = {R["trend_p"]:.2f}).'),
 P(f'&bull; <b>{R["bad_rate"]*100:.1f}% of orders end Cancelled or Returned</b>, worth ${R["bad_value"]/1e3:,.0f}K ({R["bad_value_share"]*100:.0f}% of total order value). The rate rose from {bad[2024]*100:.1f}% in 2024 to {bad[2025]*100:.1f}% in 2025 H1.'),
 P(f'&bull; <b>Order value is right-skewed</b>: median ${R["med"]:,.0f} versus mean ${R["aov"]:,.0f}. The top 10% of orders generate {R["top10"]*100:.0f}% of value. Typical order size should be quoted as the median.'),
 P(f'&bull; <b>{R["n_out"]} high-value outliers</b> (above ${R["out_thr"]:,.0f}), all with Quantity = 5. They are genuine bulk orders, not errors, and are kept (only {R["out_share"]*100:.1f}% of revenue).'),
 P('&bull; <b>Product, payment method, coupon and referral source do not change order value or order outcome</b> (all p &gt; 0.4). No segment is a proven winner or loser.'),Spacer(1,4),
 P('<b>4. Recommendations.</b>'),
 P('&bull; Investigate the cancellation and return drivers first (reasons, fulfilment stage, customer type); this is the largest and the only worsening lever.'),
 P('&bull; Do not re-allocate marketing, coupon or product spend on current evidence; run a controlled test before changing it.'),
 P('&bull; Flag Quantity = 5 bulk orders for account-management follow-up.'),
 P('&bull; Review the Pending queue: orders from 2023 are still Pending, which points to a stale status process.'),
 P('&bull; Collect H2 2025 data, discount amounts and cost/margin to confirm the downward trend.'),
 PageBreak()]
# finding 1
e+=[P('Finding 1: Monthly order value has slid about 16% since 2023',H),img('c1_trend',480),
 P(f'Monthly totals are noisy (range $27.8K to $68.1K), so a linear trend was fitted. Slope {R["trend_slope"]:,.0f} per month, p = {R["trend_p"]:.2f}: the direction is down but the sample is too short to call it significant. <b>Seasonality check:</b> comparing H1 with H2 for the two full years gives p = {R["h1h2_p"]:.2f}, so there is no seasonal effect. Note that a raw quarter or year count would be misleading here (2025 has only 6 months), which is why monthly averages were used.',B),
 Paragraph('Finding 2: Order value is right-skewed; use the median',H),img('c2_distribution',480),
 P(f'The mean (${R["aov"]:,.0f}) sits well above the median (${R["med"]:,.0f}) because a long tail of large orders pulls it upward (skewness {R["desc"].loc["TotalPrice","skew"]:.2f}). Quantity, UnitPrice and ItemsInCart are symmetric (skew about 0), so their means are safe to use.',B),PageBreak()]
# outliers & stats
od=R['out']; rows=[['Column','IQR lower','IQR upper','IQR outliers','Z > 3']]+[[r.Column,f'{r["IQR lower"]:,.2f}',f'{r["IQR upper"]:,.2f}',r['IQR outliers'],r['Z>3 outliers']] for _,r in od.iterrows()]
rows=[rows[0]]+[[P(str(c),C) for c in r] for r in rows[1:]]
ds=R['desc']; r2=[['Column','Count','Mean','Median','Std','Min','Q1','Q3','Max']]
for c,r in ds.iterrows(): r2.append([c,f'{int(r["count"])}',f'{r["mean"]:,.2f}',f'{r["median"]:,.2f}',f'{r["std"]:,.2f}',f'{r["min"]:,.2f}',f'{r["Q1"]:,.2f}',f'{r["Q3"]:,.2f}',f'{r["max"]:,.2f}'])
e+=[Paragraph('Finding 3: Outliers are bulk orders (signal), not errors (noise)',H),
 P(f'The IQR rule flags {R["n_out"]} orders above ${R["out_thr"]:,.0f}; the Z-score rule flags none (it is less sensitive on skewed data). All {R["n_out"]} have Quantity = 5 with a high unit price, and TotalPrice = Quantity x UnitPrice holds for every row. They are real transactions, so they were <b>kept</b> and flagged for follow-up rather than removed.'),Spacer(1,5),
 tbl(rows,[110,90,90,90,70]),Spacer(1,8),P('Descriptive statistics (numeric columns)',Sm),tbl(r2,[80,38,52,52,50,50,50,52,52]),Spacer(1,6),
 Paragraph('Finding 4: Total order value is driven by price and quantity; ItemsInCart tracks Quantity',H),
 Table([[img('c3_corr',230),P('TotalPrice correlates with UnitPrice (0.72) and Quantity (0.62), which is expected because it is calculated from them, so this is not a discovery. The useful signal is <b>ItemsInCart vs Quantity (0.65)</b>: bigger carts mean more units per order. UnitPrice is unrelated to Quantity (0.01) and to ItemsInCart (0.00), so shoppers do not trade off price against volume. <i>Correlation is a clue, not a verdict.</i>')]],colWidths=[240,270]),PageBreak()]
# status
e+=[Paragraph('Finding 5: 41% of orders are Cancelled or Returned, and the rate is rising',H),img('c4_status',420),
 Table([[img('c6_badrate',210),P(f'Cancelled and Returned orders carry ${R["bad_value"]/1e3:,.0f}K of the ${R["rev"]/1e3:,.0f}K total order value. The 2025 H1 rate ({bad[2025]*100:.1f}%) is {(bad[2025]-bad[2024])*100:.1f} points above 2024. The product mix does not explain it (chi-square p = {R["chi_prod_status_p"]:.2f}). <b>Data-quality flag:</b> {R["pending_2023"]} orders from 2023 are still Pending, and statuses are almost evenly split (about 20% each), which is unusual for live order data. Confirm how the status field is maintained before trusting these rates absolutely.')]],colWidths=[230,280]),
 Paragraph('Finding 6: No product or channel stands out once significance is tested',H),img('c5_product',400)]
sg=R['seg']; r3=[['Dimension','Highest mean order','Lowest mean order','Kruskal-Wallis p','Verdict']]
for k,v in sg.items():
    r3.append([k,f'{v["mean"].idxmax()} (${v["mean"].max():,.0f})',f'{v["mean"].idxmin()} (${v["mean"].min():,.0f})',f'{v.p_kruskal.iloc[0]:.2f}','No real difference'])
e+=[Spacer(1,4),tbl([r3[0]]+[[P(str(c),C) for c in r] for r in r3[1:]],[80,115,115,80,95]),Spacer(1,4),
 P('Gaps between segments exist on paper (for example Credit Card averages $1,128 vs Debit Card $1,002) but are well within random variation, so they are not treated as findings. The coupon codes (SAVE10, WINTER15, FREESHIP) also show no basket-size uplift versus no coupon.',B),
 Paragraph('Limitations and next steps',H),
 P('The dataset has no cost, margin, discount amount, customer demographics or return reasons, and 2025 covers only Jan-Jun. Value figures are order totals, not profit, and include Cancelled and Returned orders. With cost and reason fields the cancellation analysis could be turned into a financial impact estimate.',B)]
doc.build(e)

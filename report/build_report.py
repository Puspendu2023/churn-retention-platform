import json, pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table,
                                TableStyle, Image, Preformatted, KeepTogether, NextPageTemplate)
from reportlab.platypus.tableofcontents import TableOfContents
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parents[1]; FIG = ROOT / "docs" / "figures"
M = json.load(open(ROOT / "models" / "metrics.json")); CV = json.load(open(ROOT / "models" / "cv_results.json"))
NAVY = colors.HexColor("#1f4e79")
ss = getSampleStyleSheet()
B = ParagraphStyle("B", parent=ss["Normal"], fontName="Times-Roman", fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=17, textColor=NAVY, spaceBefore=4, spaceAfter=10, keepWithNext=1)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=13, textColor=NAVY, spaceBefore=10, spaceAfter=5, keepWithNext=1)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=11, spaceBefore=6, spaceAfter=3)
CAP = ParagraphStyle("CAP", parent=B, fontName="Helvetica-Oblique", fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#444"))
CEN = ParagraphStyle("CEN", parent=B, alignment=TA_CENTER)
BUL = ParagraphStyle("BUL", parent=B, leftIndent=16, bulletIndent=4, spaceAfter=3)
TC = ParagraphStyle("TC", parent=B, fontName="Helvetica", fontSize=8.2, leading=10.2, alignment=0, spaceAfter=0)
TCH = ParagraphStyle("TCH", parent=TC, fontName="Helvetica-Bold", textColor=colors.white)
CODE = ParagraphStyle("CODE", fontName="Courier", fontSize=6.6, leading=7.8)

class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=2.4*cm, rightMargin=2.2*cm, topMargin=2.3*cm, bottomMargin=2.2*cm,
                         title="AI-Powered Customer Intelligence and Retention Platform - Project Report",
                         author="Puspendu", **kw)
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate("cover", [fr], onPage=lambda c, d: None),
                               PageTemplate("body", [fr], onPage=self.deco)])
        self.fig_n = 0; self.tab_n = 0
    def deco(self, c, d):
        c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#555"))
        c.drawString(2.4*cm, 1.3*cm, "BCA-S6-MAJOR-AI-001 | AI-Powered Customer Intelligence and Retention Platform")
        c.drawRightString(A4[0]-2.2*cm, 1.3*cm, f"Page {d.page}")
        c.setStrokeColor(NAVY); c.line(2.4*cm, 1.7*cm, A4[0]-2.2*cm, 1.7*cm); c.restoreState()
    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("H1", "H2"):
            lvl = 0 if f.style.name == "H1" else 1
            t = f.getPlainText(); key = f"h{self.seq.nextf('toc')}"
            self.canv.bookmarkPage(key); self.notify("TOCEntry", (lvl, t, self.page, key))

def P(t, s=B): return Paragraph(t, s)
def bullets(items): return [Paragraph(i, BUL, bulletText="\u2022") for i in items]
def img(name, w=13*cm):
    p = FIG / name if (FIG / name).exists() else ROOT / "docs" / name
    iw, ih = PILImage.open(p).size; return Image(str(p), width=w, height=w*ih/iw)
FIGS = []; TABS = []
def fig(name, cap, w=13*cm):
    FIGS.append(cap); n = len(FIGS)
    return KeepTogether([img(name, w), P(f"Figure {n}: {cap}", CAP), Spacer(1, 6)])
def table(rows, widths, head=True, cap=None):
    data = [[Paragraph(str(c), TCH if (head and i == 0) else TC) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    t.setStyle(TableStyle(st)); out = [t]
    if cap: TABS.append(cap); out.append(P(f"Table {len(TABS)}: {cap}", CAP))
    out.append(Spacer(1, 8)); return out

pct = lambda x: f"{x*100:.1f}%"
df = pd.read_csv(ROOT / "data" / "processed" / "customer_data_clean.csv"); df["y"] = (df.Churned == "Yes").astype(int)
S = []
# ---------------- COVER ----------------
S += [Spacer(1, 1.2*cm), P("<b>PROJECT REPORT</b>", ParagraphStyle("t", parent=CEN, fontSize=14, textColor=NAVY)), Spacer(1, 1.0*cm),
      P("<b>AI-Powered Customer Intelligence<br/>and Retention Platform</b>", ParagraphStyle("t2", parent=CEN, fontSize=25, leading=31, fontName="Helvetica-Bold", textColor=NAVY)),
      Spacer(1, .6*cm), P("Anonymised client: CustomerTech India", CEN), P("Project ID: BCA-S6-MAJOR-AI-001", CEN), Spacer(1, 1.4*cm),
      P("Submitted in partial fulfilment of the requirements for the degree of", CEN),
      P("<b>Bachelor of Computer Applications (BCA)</b><br/>Semester 6 - Major Project", ParagraphStyle("t3", parent=CEN, fontSize=14, leading=19)), Spacer(1, 1.4*cm),
      P("Submitted to", CEN), P("<b>Chandigarh University<br/>Institute of Distance and Online Learning</b>", ParagraphStyle("t4", parent=CEN, fontSize=13, leading=17)), Spacer(1, 1.6*cm),
      table([["Submitted by", "Puspendu"], ["Enrolment / Student ID", "O24BCA160184"], ["Programme", "BCA (Online / Distance)"],
             ["Project guide", "______________________________"], ["Month and year", "October 2026"]], [5.5*cm, 8.5*cm], head=False),
      NextPageTemplate("body"), PageBreak()]
# ---------------- REVIEW NOTE ----------------
S += [P("Student Review Note (remove this page before submission)", ParagraphStyle("RN", parent=H2)),
      P("This report was generated with AI assistance from the supplied dataset, and every number in it comes from code in the project repository. "
        "The submission guidelines require authentic, self-owned work, so please read the whole report, rewrite the narrative in your own words, and re-run the code before you submit. "
        "Items you must complete yourself:")] + bullets([
      "Enter the guide's real name, qualification, address, mobile and email in the certificate (Annexure A) and Annexure 6; obtain the guide's and your own signatures.",
      "Write the Acknowledgement in your own words and name the people who actually helped you.",
      "Take screenshots of the running app (dashboard and prediction screens) and paste them in Chapter 9 next to the wireframe figure; the wireframes are design sketches, not screenshots.",
      "Re-run <font name='Courier'>pytest</font> and the training scripts on your machine so the Actual Result column reflects your own execution.",
      "Check whether the university requires its own cover-page template, and confirm the final page count and soft-copy upload link.",
      "The model is weak (see Chapter 8). Do not change the numbers to look better; the guide asks for honest limitations.",
      "The Dockerfile has not been built in this environment (no Docker daemon was available); build and run it yourself before claiming deployment evidence."])
S += [PageBreak()]
# ---------------- ACK ----------------
S += [P("Acknowledgement", H1),
      P("I express my sincere gratitude to my project guide, <b>______________________</b>, for the guidance, advice and encouragement provided during this project. "
        "I thank the faculty of the Institute of Distance and Online Learning, Chandigarh University, for the curriculum in Business Analytics, Software Engineering, Machine Learning and Cloud-Native Development that made this work possible."),
      P("I also thank the creators of the open-source tools used here (Python, pandas, scikit-learn, Streamlit, Plotly, Matplotlib, ReportLab and Docker), and my family and friends for their support. "
        "The dataset used in this project was supplied by the university for academic use and is anonymised."),
      Spacer(1, 1.2*cm), P("Puspendu<br/>Enrolment No. O24BCA160184", ParagraphStyle("r", parent=B, alignment=2)), PageBreak()]
# ---------------- CERTIFICATE ----------------
S += [P("Certificate from Guide (Annexure A)", H1), Spacer(1, .4*cm),
      P("This is to certify that this project entitled <b>\"AI-Powered Customer Intelligence and Retention Platform\"</b> submitted in partial fulfilment of the degree of "
        "<b>Bachelor of Computer Applications (BCA)</b> to <b>Chandigarh University</b> was done by Mr./Ms. <b>Puspendu</b>, Roll No. <b>O24BCA160184</b>, and is an authentic work carried out by him/her under my guidance. "
        "The matter embodied in this project work has not been submitted earlier for the award of any degree or diploma, to the best of my knowledge and belief."),
      Spacer(1, 2.2*cm),
      table([["_____________________________<br/>Signature of the Student", "_____________________________<br/>Signature of the Guide"],
             ["Date: _______________", "Guide name: ______________________"]], [7.5*cm, 7.5*cm], head=False),
      P("<i>Guide name, signature and date must be completed by the actual guide; they are intentionally left blank.</i>", CAP), PageBreak()]
# ---------------- TOC placeholder ----------------
toc = TableOfContents(); toc.levelStyles = [ParagraphStyle("t1", fontName="Helvetica-Bold", fontSize=10, leading=15, leftIndent=0),
                                            ParagraphStyle("t2", fontName="Helvetica", fontSize=9, leading=12, leftIndent=18)]
S += [P("Contents", ParagraphStyle("CT", parent=H1)), toc, PageBreak()]
# ---------------- SYNOPSIS ----------------
S += [P("Synopsis of the Project", H1),
      P("<b>Title of the project:</b> AI-Powered Customer Intelligence and Retention Platform"),
      P("<b>Statement of the problem.</b> CustomerTech India (anonymised) holds growing customer data but has no integrated mechanism to identify which customers are likely to leave, to explain their behaviour, or to turn the insight into timely retention action. Without it, retention effort is reactive and untargeted."),
      P("<b>Why this topic was chosen.</b> Customer churn is a high-value, well-defined business problem that combines four subjects of the programme: Business Analytics (KPIs, segmentation), Machine Learning (classification), Software Engineering (requirements, architecture, testing) and Cloud-Native Development (containerised packaging). It lets one project exercise the full path from raw data to a usable, deployable tool."),
      P("<b>Objective and scope.</b> The objective is to build a working academic prototype that (1) displays customer KPIs, (2) accepts customer attributes, (3) returns a churn-risk probability, risk band and plain-language recommended action, and (4) is packaged for cloud-ready deployment. "
        f"The scope covers one anonymised static dataset of {len(df):,} customers and 15 fields, a single scikit-learn model, a Streamlit interface and a Docker image. Live billing integration, streaming data, authentication and production monitoring are out of scope."),
      P("<b>Methodology.</b> The work followed twelve activities: problem definition, requirements, data profiling, exploratory analysis, feature preparation, model development, evaluation, architecture, prototype development, cloud-native packaging, testing and recommendations. "
        f"The overall churn rate was found to be {pct(df.y.mean())}. Three classifiers were compared by five-fold stratified cross-validation on the training set; Logistic Regression was selected for interpretability and highest recall."),
      P("<b>Hardware and software.</b> Any laptop with 4 GB RAM or more; Python 3.12, pandas, scikit-learn, Streamlit, Plotly, Matplotlib, openpyxl, joblib, pytest, Git and Docker."),
      P("<b>Testing technologies.</b> pytest for twelve automated test cases (data loading, missing values, encoding, split, training, prediction, banding, filter logic, edge cases, input validation, PII exclusion, data quality) and Streamlit's AppTest for a smoke test of the interface."),
      P("<b>Contribution and conclusion.</b> The project delivers a reproducible, documented and tested prototype and an honest evaluation. "
        f"On the held-out test set the model reached accuracy {pct(M['accuracy'])}, precision {pct(M['precision'])}, recall {pct(M['recall'])}, F1 {pct(M['f1'])} and ROC-AUC {M['roc_auc']:.3f}. "
        "These show only a weak signal in the supplied data, so predictions must be used as decision support, not as guaranteed outcomes. "
        "The most useful analytical finding is that churn rises with payment failures, support tickets and low satisfaction, which points to practical retention actions."),
      PageBreak()]
# ---------------- CH1 ----------------
S += [P("1. Objective and Scope of the Project", H1), P("1.1 Business outcome and objectives", H2),
      P("The outcome to improve is <b>customer retention</b>, measured as a lower churn rate. The specific objectives are:")] + bullets([
      "Establish a baseline churn rate and show where churn is concentrated (segment, region, age group and behavioural drivers).",
      "Build and honestly evaluate a classification model that estimates each customer's churn probability.",
      "Deliver a prototype that links analysis to action: KPI dashboard, risk prediction and recommended retention action.",
      "Design the application so that it can be containerised and scaled in a cloud environment.",
      "Produce full evidence: requirements, tests, evaluation output, architecture and source code."]) + [
      P("1.2 Key performance indicators", H2)] + table([
      ["KPI", "Definition", "Baseline (this dataset)"],
      ["Overall churn rate", "Churned customers / total customers x 100", f"{pct(df.y.mean())} ({int(df.y.sum())} of {len(df)})"],
      ["Churn rate by segment / region / age", "Same formula within each group", "Chapter 6"],
      ["Avg satisfaction of churned customers", "Mean Satisfaction_Score where Churned = Yes", f"{df[df.y==1].Satisfaction_Score.mean():.2f} (vs {df[df.y==0].Satisfaction_Score.mean():.2f} for retained)"],
      ["Model recall on churners", "TP / (TP + FN)", pct(M['recall'])],
      ["High-risk band size", "Customers scored 0.55 or above", f"{M['bands']['High']['n']} of {M['n_test']} test customers"]],
      [4.4*cm, 6.2*cm, 4.8*cm], cap="KPIs used in the project") + [
      P("1.3 Measurable target statement", H2),
      P("<b>Target:</b> reduce the churn rate from the baseline of "
        f"{pct(df.y.mean())} by targeting retention actions at customers in the High risk band. A reduction of even one percentage point corresponds to about {round(len(df)*0.01)} customers retained out of {len(df):,}. "
        "The prototype cannot prove the reduction because no live intervention is run; it provides the baseline, the targeting list and the KPI definitions against which a future campaign can be measured."),
      P("1.4 Scope and out-of-scope", H2),
      P("<b>In scope:</b> analysis of the supplied anonymised dataset; one churn model; Streamlit dashboard and prediction form; local SQLite/CSV data layer; Dockerfile; requirements, tests and documentation."),
      P("<b>Out of scope (deliberately):</b>")] + bullets([
      "Integration with live billing, CRM or messaging systems.",
      "Real-time or streaming data; the dataset is a static snapshot.",
      "User authentication, role-based access and production-grade security hardening.",
      "Measuring the real-world effect of retention campaigns (no A/B test was run).",
      "Cost-sensitive optimisation using real margin or campaign-cost data (none was supplied).",
      "Causal claims: the analysis reports association, not causation."]) + [PageBreak()]
# ---------------- CH2 ----------------
S += [P("2. Theoretical Background", H1),
      P("2.1 Customer churn", H2),
      P("Churn is the loss of a customer. Retaining an existing customer is generally cheaper than acquiring a new one, so businesses track churn rate and try to predict it in advance. Churn is modelled as a supervised <b>binary classification</b> problem: the label is Churned (Yes/No) and the inputs are demographic, transactional, support and engagement attributes."),
      P("2.2 Business analytics", H2),
      P("Descriptive analytics summarises what has happened (churn rate by group), diagnostic analytics asks where and why, and predictive analytics estimates what is likely next. This project uses all three in sequence. <b>Churn rate = churned customers / total customers x 100.</b>"),
      P("2.3 Machine-learning concepts used", H2)] + bullets([
      "<b>Logistic Regression</b> models the log-odds of churn as a linear combination of features: p = 1 / (1 + e<super>-(b0 + b1x1 + ... + bkxk)</super>). Coefficients are directly interpretable, which suits a business audience (Hosmer and Lemeshow, 2013).",
      "<b>Random Forest</b> averages many decision trees trained on resampled data and features, capturing non-linear effects at the cost of interpretability (Breiman, 2001). <b>Gradient Boosting</b> builds trees sequentially to correct earlier errors.",
      "<b>One-hot encoding</b> converts a category into binary columns so that no false order is implied; <b>standardisation</b> rescales numeric fields to zero mean and unit variance so coefficients are comparable.",
      "<b>Stratified train/test split</b> keeps the class proportion equal in both parts. <b>Cross-validation</b> estimates performance by rotating validation folds inside the training set.",
      "<b>Class weighting</b> penalises errors on the minority class (churners) more, improving recall at some cost to precision.",
      "<b>Target leakage</b> occurs when a feature contains information only available after the outcome; it inflates results and must be checked."]) + [
      P("2.4 Evaluation metrics", H2),
      P("From the confusion matrix (TP, FP, TN, FN): <b>Accuracy</b> = (TP+TN)/all; <b>Precision</b> = TP/(TP+FP); <b>Recall</b> = TP/(TP+FN); <b>F1</b> = 2PR/(P+R); <b>ROC-AUC</b> is the probability that a random churner is scored above a random non-churner (0.5 = no skill, 1.0 = perfect)."),
      P("2.5 Software engineering and cloud-native concepts", H2),
      P("Requirements are written as testable statements with acceptance criteria. Layered architecture separates the user interface, business logic and data so each can change independently. Cloud-native design favours stateless containers, externalised configuration (environment variables), horizontal scaling behind a load balancer, and centralised logging and monitoring. Docker packages the application and its dependencies into a portable image.")]
S += [PageBreak()]
# ---------------- CH3 ----------------
S += [P("3. Definition of the Problem", H1),
      P("CustomerTech India has customer, transaction, support and engagement data but cannot (a) quantify churn by group, (b) estimate an individual customer's risk, or (c) connect the estimate to a concrete action. The problem is therefore to translate a business question - <i>\"which customers are likely to leave, and what should we do?\"</i> - into a software-and-analytics solution."),
      P("<b>Users:</b> a retention or customer-success analyst who needs a dashboard and a quick risk check; a manager who needs KPIs. <b>Inputs:</b> the 14 customer attributes. <b>Outputs:</b> KPIs, churn probability, risk band (Low/Medium/High) and a recommended action."),
      P("<b>Constraints:</b> self-driven academic project of about 600 man-hours; one anonymised static dataset; no cloud credentials, so deployment is local and cloud-ready rather than cloud-hosted; predictions are decision support only."),
      P("<b>Assumptions:</b> (i) each row is one distinct customer; (ii) the Churned label is the true outcome observed after the behavioural window; (iii) the data are representative of the client's customer base. None of these can be verified from the files supplied."), PageBreak()]
# ---------------- CH4 ----------------
S += [P("4. System Analysis and Design versus User Requirements", H1), P("4.1 Requirements", H2),
      P("The five starter requirements from the supplied template were retained and extended with four of my own. Every requirement has an acceptance criterion and is traced to the module and test that satisfy it.")]
REQ = [["ID", "Requirement", "Type", "Acceptance criteria", "Status / Evidence"],
 ["FR-01", "Dashboard displays core customer KPIs", "Functional", "Dashboard shows customer count, churn rate, avg satisfaction of churned customers and avg spend; values match pandas calculations (2,200; 29.2%; 2.82; 4,815).", "Met - app.py tab 1; AppTest smoke test (TC-13)"],
 ["FR-02", "System accepts customer attributes for churn prediction", "Functional", "Form accepts all 13 model inputs; out-of-range or missing values are rejected with a clear message.", "Met - app.py tab 2; TC-10"],
 ["FR-03", "System returns churn-risk output", "Functional", "Returns probability between 0 and 1 and a band Low/Medium/High for any valid input.", "Met - predict.py; TC-06, TC-07, TC-09"],
 ["FR-04", "Dashboard can be filtered by segment and region", "Functional", "Selecting segment/region updates all KPIs and charts; empty selection shows a warning, not an error.", "Met - TC-08, TC-13"],
 ["FR-05", "System shows a recommended action for each risk band", "Functional", "Each of Low/Medium/High maps to a distinct plain-language action.", "Met - predict.ACTIONS; TC-07"],
 ["FR-06", "System displays top factors raising a selected customer's risk", "Functional", "Top three contributing features (coefficient x standardised value) are listed.", "Met - predict.top_drivers"],
 ["NFR-01", "Application should respond reliably under normal academic demo load", "Non-functional", "Single-user demo: prediction returns in under 1 second; app runs without exceptions on load.", "Met for single user - not load-tested"],
 ["NFR-02", "Solution should avoid exposing personally identifiable information", "Non-functional", "Customer_ID is excluded from model inputs and from the prediction form; dataset contains only anonymised IDs.", "Met - TC-11"],
 ["NFR-03", "Configuration must be externalised", "Non-functional", "Model path is read from the MODEL_PATH environment variable with a safe default; no secrets in code.", "Met - predict.py, Dockerfile"]]
S += table(REQ, [1.3*cm, 3.4*cm, 1.8*cm, 5.5*cm, 3.1*cm], cap="Requirements specification with acceptance criteria")
S += [P("NFR-01 is satisfied only for a single local user; no load test was run, so scalability is argued from the design (Chapter 7) rather than demonstrated.")]
S += [P("4.2 Use cases / user stories", H2)] + bullets([
      "As a retention analyst, I want to filter the dashboard by segment and region so that I can see where churn is highest.",
      "As an analyst, I want to enter a customer's attributes and get a risk band so that I can decide whether to contact them.",
      "As a manager, I want a recommended action for each risk band so that the team acts consistently.",
      "As a data owner, I want personal identifiers kept out of the tool so that privacy is protected."])
S += [P("4.3 Dataset understanding and data quality", H2),
      P(f"The dataset (Customer Data sheet) has <b>{len(df):,} rows and 15 columns</b>. Customer_ID is unique (no duplicate IDs or rows). There are <b>no missing values</b>, no negative numbers, Discount_Usage_Pct lies within 0-80 (never outside 0-100) and Satisfaction_Score lies within 1-5. "
        "The target is imbalanced but not extreme: 1,557 retained (70.8%) and 643 churned (29.2%).")]
prof = [["Field", "Type", "Observed range / values", "Mean"]]
for c, t in [("Tenure_Months","Integer"),("Monthly_Spend_INR","Numeric"),("Transactions_90D","Integer"),("Support_Tickets_90D","Integer"),("Avg_Response_Hours","Numeric"),
             ("Satisfaction_Score","Integer"),("App_Logins_30D","Integer"),("Days_Since_Last_Purchase","Integer"),("Discount_Usage_Pct","Percentage"),("Payment_Failures_90D","Integer")]:
    prof.append([c, t, f"{df[c].min():g} to {df[c].max():g}", f"{df[c].mean():.2f}"])
for c in ["Age_Group", "Region", "Customer_Segment"]:
    prof.append([c, "Category", ", ".join(sorted(df[c].unique())), "-"])
S += table(prof, [4.6*cm, 2.2*cm, 6.6*cm, 2*cm], cap="Profile of the dataset (observed values)")
S += [P("<b>Observation on the supplied schema.</b> The build prompt described four age bands and four regions, but the actual file has <b>five age groups</b> (18-24, 25-34, 35-44, 45-54, 55+) and <b>five regions</b> (adding South). The project follows the actual data."),
      P("<b>Data-quality risks and limitations.</b>")] + bullets([
      "Class imbalance (29.2% churn): accuracy alone is misleading because predicting \"No\" for everyone scores 70.7% on the test set.",
      "Several numeric fields look uniformly distributed (for example Avg_Response_Hours 1-30, Discount_Usage_Pct 0-80), which suggests the data may be synthetic or heavily anonymised; real-world patterns may be weaker or different.",
      "Support_Tickets_90D has a narrow range (0-7) and Payment_Failures_90D (0-4), so these behave almost like categories.",
      "The dataset is a single snapshot; time order is unknown, so a time-based split and drift checks were not possible.",
      "Whether the behavioural fields were measured before the churn event is assumed, not verified (leakage risk discussed in 4.5)."]) + [Spacer(1,4), fig("class_balance.png", "Class balance of the target variable", 6.5*cm)]
S += [P("4.4 Candidate predictors (no causal claim)", H2)] + bullets([
      "<b>Payment_Failures_90D, Support_Tickets_90D, Avg_Response_Hours:</b> friction with billing and service may be associated with leaving.",
      "<b>Satisfaction_Score:</b> a direct sentiment measure, expected to be associated with retention.",
      "<b>Days_Since_Last_Purchase, Transactions_90D, App_Logins_30D:</b> recency and engagement; falling activity often precedes churn.",
      "<b>Tenure_Months, Monthly_Spend_INR, Discount_Usage_Pct:</b> relationship length, value and price sensitivity.",
      "<b>Age_Group, Region, Customer_Segment:</b> context variables used to compare groups and as model inputs."])
S += [P("4.5 Feature preparation and leakage check", H2)] + table([
      ["Step", "Decision", "Justification"],
      ["Identifier", "Customer_ID excluded", "Unique identifier, not predictive, and a privacy risk (NFR-02)."],
      ["Categorical fields", "One-hot encoding of Age_Group, Region, Customer_Segment (handle_unknown=ignore)", "Regions and segments have no natural order; avoids implying one. Unknown categories at prediction time do not crash the model."],
      ["Numeric fields", "StandardScaler on all 10 numeric inputs", "Logistic Regression is scale-sensitive and standardised coefficients are comparable."],
      ["Missing values", "Median imputation implemented, 0 values needed", "None are present, but the pipeline remains robust."],
      ["Target", "Churned mapped Yes=1, No=0", "Binary classification target."],
      ["Final feature set", "13 raw fields -> 23 model columns (3 categories become 13 dummies + 10 numeric)", "No other fields were dropped."]],
      [3*cm, 6*cm, 6.4*cm], cap="Feature preparation decisions") + [
      P("<b>Target-leakage check.</b> Each feature describes behaviour in a window (90 days or 30 days) or a status (tenure, latest satisfaction, recency). None is by definition a post-churn event such as a cancellation code or final-bill field. "
        "However, Days_Since_Last_Purchase and Satisfaction_Score could in principle be recorded <i>after</i> a customer has already disengaged. This cannot be verified from the data dictionary, so it is listed as a limitation rather than assumed away.")]
S += [PageBreak()]
# ---------------- CH5 EDA ----------------
S += [P("5. Exploratory Business Analytics", H1),
      P(f"<b>Overall churn rate = 643 / 2,200 x 100 = {pct(df.y.mean())}.</b> Differences between segments, regions and age groups are small; the strongest patterns appear in behavioural fields."),]
def grp(c):
    g = df.groupby(c).y.agg(["mean", "sum", "count"]); return [[str(i), int(r['count']), int(r['sum']), pct(r['mean'])] for i, r in g.iterrows()]
S += table([["Customer segment", "Customers", "Churned", "Churn rate"]] + grp("Customer_Segment"), [5*cm, 3*cm, 3*cm, 3*cm], cap="Churn rate by customer segment")
S += table([["Region", "Customers", "Churned", "Churn rate"]] + grp("Region"), [5*cm, 3*cm, 3*cm, 3*cm], cap="Churn rate by region")
S += table([["Age group", "Customers", "Churned", "Churn rate"]] + grp("Age_Group"), [5*cm, 3*cm, 3*cm, 3*cm], cap="Churn rate by age group")
S += [fig("churn_segment.png", "Churn rate by customer segment", 10.5*cm),
      P("<b>Business interpretation.</b> Growth customers churn slightly more (30.1%) than Premium (29.6%) and Value (27.9%), but the spread is about two percentage points. Segment alone is not a strong lever; it should not be the main targeting rule."),
      fig("churn_region.png", "Churn rate by region", 10.5*cm),
      P("<b>Business interpretation.</b> East has the highest churn (32.3%) and Central the lowest (26.8%), a gap of about five points. East is a candidate for a regional review of service and delivery, though with roughly 440 customers per region this gap could partly be chance."),
      fig("churn_payfail.png", "Churn rate by payment failures in the previous 90 days", 10.5*cm),
      P("<b>Business interpretation.</b> This is the clearest pattern: churn is 21.9% with no payment failure and 40.0% with four failures, almost double. Payment friction (failed cards, retries, billing errors) is strongly associated with leaving and is actionable."),
      fig("sat_dist.png", "Satisfaction score distribution split by churn status", 10.5*cm),
      fig("churn_sat.png", "Churn rate by satisfaction score", 10.5*cm),
      P("<b>Business interpretation.</b> Churn is highest at scores 1 and 2 (34.6% and 37.9%) and lowest at 4 (21.7%). The pattern is not perfectly smooth: score 5 shows 26.8%, higher than score 4, so satisfaction is informative but not a clean one-way predictor."),
      P("<b>Support tickets.</b> Churn is 21.6-25.4% for customers with 0-3 tickets but 33.3-37.0% for those with 4 or more, which suggests a threshold effect around four tickets in 90 days."),
      fig("corr.png", "Correlation of numeric fields with churn", 11*cm),
      P("<b>Interpretation.</b> All correlations are small in absolute terms. The largest are Payment_Failures_90D (+0.14), Support_Tickets_90D (+0.10), Satisfaction_Score (-0.10) and Days_Since_Last_Purchase (+0.08). Tenure, spend and response time are close to zero. This foreshadows a modest ceiling on model accuracy."),
      PageBreak()]
# ---------------- CH6 MODEL ----------------
S += [P("6. Machine Learning Model Development and Evaluation", H1), P("6.1 Algorithm selection", H2),
      P("Three classifiers were compared using five-fold stratified cross-validation on the 1,760-row training set only. The test set was not used for selection.")]
rows = [["Model", "ROC-AUC", "Recall", "Precision", "F1", "Accuracy"]]
for k, v in CV.items(): rows.append([k, f"{v['roc_auc']:.3f}", f"{v['recall']:.3f}", f"{v['precision']:.3f}", f"{v['f1']:.3f}", f"{v['accuracy']:.3f}"])
S += table(rows, [4.6*cm, 2*cm, 2*cm, 2.2*cm, 2*cm, 2.2*cm], cap="Cross-validation results on the training set (mean of 5 folds)")
S += [P("<b>Choice: Logistic Regression with balanced class weights.</b> It ties Random Forest on ROC-AUC (0.625), has the highest recall (0.588) - important because missing a churner is costly - and is interpretable, which matters because the output must justify an action to a business user. "
        "The dataset is small (2,200 rows) with mostly numeric inputs and weak signals, so a more complex model offers little benefit. Gradient Boosting at the default 0.5 threshold almost never predicted churn (recall 0.08), so it is unsuitable without threshold tuning."),
      P("6.2 Train/test split", H2),
      P("An 80/20 <b>stratified</b> split with random_state 42 gave 1,760 training and 440 test rows. Stratification keeps the churn rate at 29.2% in training and 29.3% in test, which matters because the minority class is only 29%. "
        "80/20 keeps enough training data for 23 features while leaving 129 churners in the test set for evaluation. Model parameters: LogisticRegression(max_iter=1000, class_weight='balanced'), preceded by one-hot encoding and standardisation in a single scikit-learn Pipeline saved to models/churn_model.pkl."),
      P("6.3 Test-set results", H2)]
S += table([["Metric", "Value", "Business interpretation"],
  ["Accuracy", pct(M['accuracy']), f"{M['tp']+M['tn']} of {M['n_test']} customers classified correctly. This is <b>below</b> the {pct(M['majority_baseline_accuracy'])} obtained by predicting 'stays' for everyone, because the model deliberately flags more customers to catch churners."],
  ["Precision", pct(M['precision']), f"Of {M['tp']+M['fp']} customers flagged as likely to churn, only {M['tp']} actually did, so about two in three retention contacts go to customers who would have stayed."],
  ["Recall", pct(M['recall']), f"The model finds {M['tp']} of {M['tp']+M['fn']} real churners (about half); {M['fn']} churners are missed."],
  ["F1-score", pct(M['f1']), "Balance of precision and recall; moderate-to-low."],
  ["ROC-AUC", f"{M['roc_auc']:.3f}", "Only slightly above 0.5 (random). A bootstrap 95% interval on the test set is about 0.50-0.62, so the true ability is uncertain."]],
  [2.4*cm, 2*cm, 11*cm], cap="Model evaluation on the held-out test set")
S += [fig("confusion_matrix.png", f"Confusion matrix on the test set: TN={M['tn']}, FP={M['fp']}, FN={M['fn']}, TP={M['tp']}", 8*cm),
      fig("roc_curve.png", "ROC curve on the test set", 8*cm),
      P("6.4 Which error is more costly?", H2),
      P("<b>A false negative is usually more costly.</b> A false negative is a customer who really churns but is not flagged, so the company loses that customer's future revenue (average spend is about INR 4,815 per month) and gets no chance to intervene. "
        "A false positive costs only a retention contact or small incentive offered to a customer who would have stayed. Unless the incentive is very expensive, recall deserves priority over precision, which is why class weights were used. The balance should be revisited with real campaign-cost data."),
      P("6.5 Risk bands", H2),
      P("Probabilities are grouped into Low (below 0.35), Medium (0.35 to below 0.55) and High (0.55 or above). The thresholds are my design choice, not derived from cost data.")]
S += table([["Band", "Test customers", "Actual churn rate"]] + [[b, v['n'], pct(v['actual_churn_rate'])] for b, v in M['bands'].items()], [4*cm, 4*cm, 4*cm], cap="Actual churn rate by predicted risk band (test set)")
S += [P("The ordering is correct (22.1% to 30.2% to 32.1%), but the separation between Medium and High is small. The model gives a modest ranking signal, not a precise one."),
      P("6.6 Interpretation of coefficients", H2), fig("coefficients.png", "Logistic Regression coefficients on standardised features", 11.5*cm),
      P("The strongest risk-raising features are Payment_Failures_90D (+0.34), Support_Tickets_90D (+0.25) and Days_Since_Last_Purchase (+0.23); the strongest protective features are Satisfaction_Score (-0.22) and Region_Central (-0.22). "
        "This agrees with the exploratory findings and is reassuring, but coefficients show association, not cause."),
      P("6.7 Model limitations", H2)] + bullets([
      "Weak signal: the test ROC-AUC (0.558) is lower than cross-validated AUC (0.625); with 440 test rows the difference is within sampling noise but the performance is clearly modest.",
      "Accuracy is below the naive baseline; the model should be judged on recall and ranking, not accuracy.",
      "No hyper-parameter tuning or threshold optimisation was done; a small gain may be possible but the data appear to contain limited predictive signal.",
      "Single static snapshot; performance on future data is unknown and drift is not monitored.",
      "Predictions are decision support and must be combined with human judgement."]) + [PageBreak()]
# ---------------- CH7 ARCH ----------------
S += [P("7. System Design, Planning and Process Logic", H1), P("7.1 Architecture", H2),
      P("The system uses a layered design: a Streamlit UI layer, a business-logic and model-serving layer, a data layer and an offline training pipeline."),
      fig("architecture_diagram.png", "System architecture", 14*cm),
      P("<b>Module boundaries.</b> data_prep.py (data layer) has no dependency on predict.py or app.py; predict.py (business logic) does not import the UI; app.py is the only module that imports Streamlit. If the system were split into services, a REST API (for example FastAPI exposing POST /predict) would sit between app.py and predict.py.")]
S += [P("7.2 Data flow diagrams", H2), fig("dfd0.png", "Context-level (Level 0) data flow diagram", 13*cm), fig("dfd1.png", "Level 1 data flow diagram", 14*cm),
      P("7.3 Entity-relationship diagram", H2), fig("erd.png", "Entity-relationship diagram", 13*cm)]
S += [P("7.4 System planning (PERT chart)", H2),
      P("The project of roughly 600 man-hours was planned as the activities below. Durations are planning estimates in working days, not measured values.")]
S += table([["Activity", "Description", "Predecessor", "Est. days"],
  ["A", "Problem definition and requirements", "-", "4"], ["B", "Data profiling and exploratory analysis", "A", "6"], ["C", "Feature preparation and model development", "B", "6"],
  ["D", "Model evaluation and interpretation", "C", "3"], ["E", "Application prototype build", "D", "7"], ["F", "Docker packaging and cloud design", "D", "3"],
  ["G", "Testing and validation", "E", "3"], ["H", "Final report and review", "F, G", "6"]], [2*cm, 8*cm, 3*cm, 2.4*cm], cap="Activity list for PERT chart")
S += [fig("pert.png", "PERT chart (critical path A-B-C-D-E-G-H, 35 days of path duration)", 14*cm)]
S += [P("7.5 Process logic of each module", H2)] + table([
  ["Module", "Process logic"],
  ["data_prep.py", "1) Read the Excel file. 2) validate(): count missing values, duplicate IDs, out-of-bound values. 3) clean(): strip text, drop duplicate IDs, median-impute numeric gaps. 4) Provide ColumnTransformer (one-hot + scaler) and stratified split."],
  ["train_model.py", "1) Clean data and split 80/20 stratified. 2) For each candidate: 5-fold stratified CV on training data. 3) Fit chosen pipeline on full training set. 4) Save to models/churn_model.pkl and CV results to JSON."],
  ["evaluate_model.py", "1) Load model. 2) Predict probabilities on test set; threshold 0.5. 3) Compute accuracy, precision, recall, F1, AUC, confusion matrix, risk-band table. 4) Save metrics.json and figures."],
  ["predict.py", "1) validate_input(): all fields present and within bounds, else ValueError. 2) predict_proba. 3) risk_band(): below 0.35 Low, below 0.55 Medium, else High. 4) Return probability, band, action. 5) top_drivers(): coefficient x standardised value, top three."],
  ["app.py", "Tab 1: load data, apply segment/region filters, show KPIs and charts, warn if no rows. Tab 2: collect inputs in a form; on submit call predict_one and display probability, band, action and top factors; show validation errors."]],
  [3.2*cm, 12.2*cm], cap="Process logic per module")
S += [PageBreak()]
# ---------------- CH8 IMPLEMENTATION ----------------
S += [P("8. Methodology, Implementation and Cloud-Native Design", H1), P("8.1 Methodology", H2),
      P("An iterative, evidence-driven method was used: define the problem, specify requirements, profile data, explore, prepare features, model, evaluate, design, build, package, test, and recommend. Each step produced a stored artefact (document, figure, script or metric file) and the repository was committed to Git after each stage."),
      P("8.2 Hardware and software", H2)] + table([
      ["Item", "Specification"],
      ["Hardware", "Standard laptop/desktop, 4 GB RAM or more, no GPU required."],
      ["Operating system", "Windows, macOS or Linux (development used Ubuntu 24)."],
      ["Language and libraries", "Python 3.12; pandas, numpy, scikit-learn, matplotlib, plotly, openpyxl, joblib."],
      ["Application framework", "Streamlit."],
      ["Data store", "Excel/CSV files; SQLite is the planned persistent store."],
      ["Testing", "pytest; Streamlit AppTest."],
      ["Version control / packaging", "Git; Docker."]], [4.2*cm, 11.2*cm], cap="Hardware and software")
S += [P("8.3 Cloud-native design and packaging", H2),
      P("The provided Dockerfile builds a slim Python 3.12 image, installs dependencies, copies the source, model artefact and processed data, runs as a non-root user, exposes port 8501 and defines a health check. "
        "<b>This Dockerfile has not been built or run in the environment where this report was prepared;</b> it must be built locally (<font name='Courier'>docker build -t churn-platform .</font> then <font name='Courier'>docker run -p 8501:8501 churn-platform</font>) before it is cited as deployment evidence."),
      P("<b>Components and needs.</b> Application service: stateless Streamlit container. Model artefact: churn_model.pkl, mounted as a read-only volume or pulled from object storage at start-up. Configuration: environment variable MODEL_PATH (and any future settings) rather than hard-coded values. Persistent data: customer data on a mounted volume or managed database, never baked into the container for production."),
      P("<b>Scalability.</b> Because the container is stateless, several replicas can run behind a load balancer; scaling is horizontal and driven by CPU or request count. Model inference for one record is fast (well under a second locally), so the first bottleneck would be data access, not the model."),
      P("<b>Secrets.</b> Credentials (database passwords, API keys, if later added) would be injected at runtime from the platform's secret manager, never committed to Git (.env is in .gitignore)."),
      P("<b>Monitoring and logging.</b> Write structured logs to stdout for collection by the platform; track request count, latency and errors; monitor the share of customers in each risk band and the proportion of invalid inputs. Monitor data drift and periodically compare predictions with actual churn to decide when to retrain."),
      P("8.4 Maintenance and evaluation", H2)] + bullets([
      "<b>Retraining:</b> retrain when new labelled data is available or when monitored recall falls; run train_model.py then evaluate_model.py.",
      "<b>Versioning:</b> keep each model artefact and metrics.json under a version tag in Git or object storage.",
      "<b>Back-up:</b> back up the data volume and model artefacts on a schedule; the code is protected by Git.",
      "<b>Regression testing:</b> run pytest before each release; add tests for each defect found.",
      "<b>Evaluation:</b> track the KPIs in Table 1 on each refresh and compare with the baseline churn rate."])
S += [P("8.5 Cost and benefit analysis", H2),
      P("<b>Costs.</b> All tools are open source, so licence cost is zero. The main cost is student effort of about 600 man-hours (per the submission guidelines) plus ordinary computing and an internet connection. Running costs for a small cloud deployment (one container and storage) would be modest but were not quoted, so no rupee figure is claimed."),
      P("<b>Benefits (illustrative, assumption-based).</b> Average monthly spend in the dataset is INR 4,815. If a retention programme guided by the tool saved 1% of customers (22 of 2,200), the revenue retained would be about 22 x 4,815 = <b>INR 105,900 per month</b>, before the cost of incentives. "
        "This is a worked example of the arithmetic, not a forecast: the effect size, campaign cost and customer margin are unknown. Qualitative benefits include consistent, documented targeting and a reusable analytics pipeline."), PageBreak()]
# ---------------- CH9 SCREENS ----------------
S += [P("9. Input and Output Screen Design", H1),
      P("The interface has two tabs. The wireframes below are design sketches; replace or supplement them with real screenshots from the running application."),
      fig("wireframes.png", "Screen designs: KPI dashboard and churn risk prediction", 15*cm),
      P("<b>Inputs:</b> sidebar multi-select for segment and region; prediction form with three dropdowns (age group, region, segment), nine numeric inputs and a satisfaction slider (1-5). <b>Outputs:</b> four KPI tiles, three bar charts, churn probability, colour-coded risk band, recommended action and top contributing factors."),
      P("<b>Worked examples produced by the prototype</b> (illustrative customers I constructed to show the two extremes, not real records):")]
S += table([["Customer profile", "Probability", "Band", "Top factors"],
  ["18-24, East, Growth, tenure 6, 6 tickets, 4 payment failures, satisfaction 2, 100 days since purchase", "78.5%", "High", "Payment_Failures_90D, Support_Tickets_90D, Days_Since_Last_Purchase"],
  ["45-54, Central, Value, tenure 48, 1 ticket, 0 payment failures, satisfaction 4, 15 days since purchase", "16.9%", "Low", "(no strong risk factor)"]],
  [7.4*cm, 2*cm, 1.5*cm, 4.5*cm], cap="Example predictions")
S += [P("9.1 Process flow for the user", H2),
      P("The user opens the dashboard, filters by segment or region to see the churn rate, switches to the prediction tab, enters or selects customer attributes, presses Predict, reads the probability and band, and follows the recommended action. Map of features to requirements: KPI tiles - FR-01; filters - FR-04; form - FR-02; probability and band - FR-03; action text - FR-05; top factors - FR-06."),
      P("9.2 Security aspects, access rights, back-up and controls (operational manual summary)", H2)] + bullets([
      "<b>Install:</b> create a virtual environment, <font name='Courier'>pip install -r requirements.txt</font>, run <font name='Courier'>python -m src.data_prep</font>, <font name='Courier'>python -m src.train_model</font>, then <font name='Courier'>streamlit run src/app.py</font>.",
      "<b>Privacy:</b> only anonymised IDs exist; Customer_ID is not used by the model or form; no data are sent to external services.",
      "<b>Access rights:</b> the prototype has no login. In production, access should be restricted by role (analyst: view and predict; administrator: retrain and deploy) via the organisation's identity provider.",
      "<b>Input controls:</b> numeric bounds and required fields are enforced before prediction.",
      "<b>Back-up:</b> copy models/ and data/ regularly; use Git for code.",
      "<b>Troubleshooting:</b> if the app reports a missing model file, run train_model.py; if the data file is missing, place customer_data.xlsx in data/raw/."])
S += [PageBreak()]
# ---------------- CH10 TESTING ----------------
S += [P("10. Testing and Validation", H1),
      P("<b>Methodology.</b> Black-box functional tests of each module and white-box checks of data handling were automated in pytest (file tests/test_platform.py). All twelve cases were executed in the development environment and passed (12 passed in about 4.5 seconds). A thirteenth check used Streamlit's AppTest to load the full app without exceptions and apply a filter.")]
TCS = [["ID", "Module", "Test scenario", "Expected result", "Actual result", "Pass/Fail"],
 ["TC-01", "Data loading", "Load customer_data.xlsx", "2,200 rows and 15 columns; first column Customer_ID", "As expected", "Pass"],
 ["TC-02", "Cleaning", "Insert a missing Monthly_Spend_INR value and run clean()", "No missing values remain", "No missing values", "Pass"],
 ["TC-03", "Encoding", "Fit the preprocessor", "Customer_ID absent; 23 output columns", "23 columns, no ID", "Pass"],
 ["TC-04", "Split", "Stratified 80/20 split", "440 test rows; churn rate within 1 point of train", "440 rows; 29.3% vs 29.2%", "Pass"],
 ["TC-05", "Training", "Fit Logistic Regression pipeline", "Trains without error, supports predict_proba", "Trained successfully", "Pass"],
 ["TC-06", "Prediction", "Predict a valid customer", "Probability in [0,1] and a valid band", "Valid output", "Pass"],
 ["TC-07", "Risk logic", "Probabilities 0.1, 0.4, 0.9", "Low, Medium, High; action text present", "Low, Medium, High; action returned", "Pass"],
 ["TC-08", "Filtering", "Filter Premium + West", "Non-empty subset containing only Premium", "Subset returned correctly", "Pass"],
 ["TC-09", "Edge case", "New customer with tenure 0", "Valid probability returned", "Valid probability", "Pass"],
 ["TC-10", "Validation", "Satisfaction 9; missing Region", "ValueError raised for each", "ValueError raised", "Pass"],
 ["TC-11", "Privacy", "Check feature list", "Customer_ID not a model feature", "Not present", "Pass"],
 ["TC-12", "Data quality", "Run validate() on raw data", "0 missing, 0 duplicate IDs, 0 out-of-bound discounts", "All zero", "Pass"],
 ["TC-13", "UI smoke", "Load app via AppTest; filter to Premium", "No exceptions; KPIs update (2,200 to 729 customers)", "No exceptions; 729 customers, 29.6%", "Pass"]]
S += table(TCS, [1.2*cm, 1.9*cm, 3.7*cm, 3.9*cm, 3.0*cm, 1.4*cm], cap="Test report")
S += [P("<b>Defects and limitations found.</b> (1) The first run of the app produced deprecation warnings for the Streamlit parameter use_container_width; this was corrected by switching to width='stretch'. "
        "(2) Testing showed that top_drivers can list a zero-contribution dummy variable for low-risk customers (for example Age_Group_18-24 at 0.00), which is not informative; it is documented as a limitation of ranking by contribution when no strong driver exists. "
        "(3) Load, browser and multi-user tests, and a Docker build test, were not performed."), PageBreak()]
# ---------------- CH11 FINDINGS ----------------
S += [P("11. Findings, Recommendations and Conclusion", H1), P("11.1 Evidence-based findings", H2)]
S += table([["No.", "Finding", "Evidence"],
  ["1", "Payment failures are strongly associated with churn: 21.9% churn with none versus 40.0% with four failures.", "Figure 'Churn rate by payment failures'; largest model coefficient (+0.34)"],
  ["2", "Low satisfaction and many support tickets coincide with higher churn: scores 1-2 show 34.6-37.9% churn versus 21.7% at score 4; four or more tickets show 33-37% versus 22-25% for 0-3.", "Satisfaction and ticket analyses; coefficients -0.22 and +0.25"],
  ["3", f"The model gives only a modest signal: test ROC-AUC {M['roc_auc']:.3f}, recall {pct(M['recall'])}, precision {pct(M['precision'])}; actual churn rises from 22.1% (Low band) to 32.1% (High band).", "Evaluation table, confusion matrix and risk-band table"]],
  [1*cm, 8.6*cm, 5.8*cm], cap="Findings and evidence")
S += [P("11.2 Recommended retention actions", H2)] + bullets([
      "<b>Fix payment friction first:</b> contact customers with two or more payment failures, offer alternative payment methods and automatic retry or reminders. Expected outcome: lower churn in the group where it is highest.",
      "<b>Proactive service recovery:</b> call customers with four or more support tickets and low satisfaction (1-2) within a set time, and track resolution time. Expected outcome: improved satisfaction and fewer exits.",
      "<b>Targeted outreach by risk band:</b> prioritise the High band for personal contact and the Medium band for low-cost digital offers, and run a controlled pilot (a contacted group versus a comparison group) to measure the real effect. Expected outcome: measured retention uplift and evidence for a cost-benefit decision."])
S += [P("11.3 Future technical enhancements", H2)] + bullets([
      "<b>Real-time data pipeline and monitoring:</b> stream transaction and support events, refresh scores automatically and monitor drift and recall.",
      "<b>Richer explainability and modelling:</b> add SHAP-based per-customer explanations, tune thresholds with real campaign-cost data, and test time-based validation when dated data is available.",])
S += [P("11.4 Conclusion", H2),
      P("The project delivers a reproducible prototype that goes from raw data to KPIs, model, prediction, recommendation, tests and a container design. It also shows honestly that the supplied data support only a modest churn signal. "
        "The behavioural patterns - payment failures, support tickets and low satisfaction - are the most useful business insight, and the prototype is a sound base for a real deployment once richer, time-stamped data and campaign-cost information are available."), PageBreak()]
# ---------------- ANNEXURES ----------------
S += [P("Annexure 1: Background of the Organisation", H1), P("Not applicable. The client, CustomerTech India, is an anonymised organisation provided by the university for an academic case study."),
      P("Annexure 2: Data Dictionary", H1)]
dd = [["Data name", "Aliases", "Length / size", "Type", "Definition", "Observed values"],
 ["Customer_ID", "-", "6 characters", "Alpha-numeric", "Unique anonymised customer identifier", "C00001 to C02200"],
 ["Age_Group", "Age band", "5 categories", "Alpha", "Customer age band", "18-24, 25-34, 35-44, 45-54, 55+"],
 ["Region", "-", "5 categories", "Alpha", "Operating region", "Central, East, North, South, West"],
 ["Customer_Segment", "Segment", "3 categories", "Alpha", "Commercial customer segment", "Growth, Premium, Value"],
 ["Tenure_Months", "Tenure", "Integer", "Numeric", "Months since acquisition", "1 to 60"],
 ["Monthly_Spend_INR", "Spend", "Integer", "Numeric", "Average monthly spend (INR)", "605 to 8,996"],
 ["Transactions_90D", "-", "Integer", "Numeric", "Transactions in last 90 days", "0 to 18"],
 ["Support_Tickets_90D", "-", "Integer", "Numeric", "Support tickets in last 90 days", "0 to 7"],
 ["Avg_Response_Hours", "-", "Decimal", "Numeric", "Average support response time (hours)", "1.0 to 30.0"],
 ["Satisfaction_Score", "CSAT", "Integer 1-5", "Numeric", "Latest satisfaction rating", "1 to 5"],
 ["App_Logins_30D", "-", "Integer", "Numeric", "App logins in last 30 days", "0 to 35"],
 ["Days_Since_Last_Purchase", "Recency", "Integer", "Numeric", "Days since last purchase", "1 to 120"],
 ["Discount_Usage_Pct", "-", "Integer", "Numeric (%)", "Share of purchases using discounts", "0 to 80"],
 ["Payment_Failures_90D", "-", "Integer", "Numeric", "Failed payments in last 90 days", "0 to 4"],
 ["Churned", "Target", "3 characters", "Binary (Yes/No)", "Target variable: churn", "Yes 643; No 1,557"]]
S += table(dd, [3.4*cm, 1.6*cm, 1.9*cm, 2.1*cm, 3.6*cm, 3*cm], cap="Data dictionary")
S += [P("Annexure 3: List of Abbreviations, Figures and Tables", H1),
      P("<b>Abbreviations:</b> AUC - Area Under the Curve; BCA - Bachelor of Computer Applications; CSAT - Customer Satisfaction; CV - Cross-Validation; DFD - Data Flow Diagram; ERD - Entity-Relationship Diagram; FN/FP/TN/TP - false negative/false positive/true negative/true positive; FR/NFR - functional/non-functional requirement; INR - Indian Rupee; KPI - Key Performance Indicator; PERT - Program Evaluation and Review Technique; PII - Personally Identifiable Information; ROC - Receiver Operating Characteristic; UI - User Interface."),
      P("<b>List of figures:</b>")] + [P(f"Figure {i+1}: {c}", TC) for i, c in enumerate(FIGS)] + [Spacer(1, 6), P("<b>List of tables:</b>")] + [P(f"Table {i+1}: {c}", TC) for i, c in enumerate(TABS)]
S += [PageBreak(), P("Annexure 4: References", H1)] + [P(x, B) for x in [
 "[1] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, 2011, pp. 2825-2830.",
 "[2] W. McKinney, \"Data Structures for Statistical Computing in Python,\" Proceedings of the 9th Python in Science Conference, 2010, pp. 56-61.",
 "[3] D. W. Hosmer, S. Lemeshow and R. X. Sturdivant, Applied Logistic Regression, 3rd ed., Wiley, 2013.",
 "[4] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, 2001, pp. 5-32.",
 "[5] Streamlit documentation, https://docs.streamlit.io",
 "[6] scikit-learn user guide, https://scikit-learn.org/stable/user_guide.html",
 "[7] Docker documentation, https://docs.docker.com",
 "[8] Chandigarh University, Project Submission Guidelines and BCA-S6-MAJOR-AI-001 Student Project Workbook and Development Guide (supplied course documents).",
 "[9] Client Data Set, Data Dictionary and templates supplied with the project (anonymised, academic use only)."]]
S += [P("Annexure 5: Soft Copy of the Project", H1), P("The complete source code, data, model artefact, documentation and this report are provided in the repository archive churn-retention-platform.zip. Upload it using the drive link shared by the university."),
      P("Annexure 6: Guide Details", H1)] + table([["Guide name", "______________________________"], ["Full address", "______________________________"], ["Qualification", "______________________________"],
      ["Mobile", "______________________________"], ["Email", "______________________________"]], [4*cm, 10*cm], head=False)
S += [P("Annexure 7: Certificate from Guide", H1), P("See the Certificate from Guide at the front of this report (Annexure A format).")]
# ---------------- CODE PRINTOUT ----------------
S += [PageBreak(), P("Annexure 8: Source Code Printout", H1)]
for f in ["src/data_prep.py", "src/train_model.py", "src/evaluate_model.py", "src/predict.py", "src/app.py", "tests/test_platform.py", "Dockerfile"]:
    txt = (ROOT / f).read_text().replace("\t", "    ")
    S += [P(f"<b>{f}</b>", H3), Preformatted(txt, CODE), Spacer(1, 8)]

def flat(x):
    for i in x:
        if isinstance(i, list): yield from flat(i)
        else: yield i
S = list(flat(S))
doc = Doc(str(ROOT / "report" / "Project_Report_BCA-S6-MAJOR-AI-001.pdf"))
doc.multiBuild(S)
print("built")

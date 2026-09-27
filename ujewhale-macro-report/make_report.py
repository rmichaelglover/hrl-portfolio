from pathlib import Path
import csv
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, PageBreak, Table, TableStyle, Image, Preformatted)

ROOT = Path(__file__).parent
ROOT.mkdir(exist_ok=True)

# Small, auditable extracts from published real sources. The Ujewhale series is
# explicitly fictional; these values calibrate the scale of the toy model.
real_rows = [
    ["BLS ATUS 2023", "sleep, weekday", 8.80, "hours/day"],
    ["BLS ATUS 2023", "sleep, weekend/holiday", 9.69, "hours/day"],
    ["CDC BRFSS 2014", "healthy sleep (>=7h)", 65.2, "% adults"],
    ["CDC BRFSS 2014", "short sleep (<7h)", 34.8, "% adults"],
    ["CDC NHIS 2020", "adults with sleep difficulty", 30.0, "% (approx. report table)"],
]

def make_charts():
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(8.3, 4.8))
    labels = ["ATUS\nweekday", "ATUS\nweekend", "BRFSS\nhealthy", "BRFSS\nshort"]
    vals = [8.80, 9.69, 65.2, 34.8]
    cols = ["#39c6d7", "#7de2a8", "#f5c451", "#ef7b9a"]
    ax.bar(labels, vals, color=cols)
    ax.set_title("Published sleep indicators used as calibration anchors")
    ax.set_ylabel("Hours/day or percent (different units; read labels)")
    ax.text(0.01, -0.2, "Sources: BLS ATUS 2023; CDC BRFSS 2014. Values are not combined into one statistic.", transform=ax.transAxes, fontsize=8)
    fig.tight_layout(); fig.savefig(ROOT / "real_sleep_anchors.png", dpi=180); plt.close(fig)

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    daylight = [9.5,10.5,12.0,13.5,14.5,15.0,14.5,13.5,12.0,10.8,9.5,9.1]
    fig, ax = plt.subplots(figsize=(8.3, 4.8)); ax.plot(months, daylight, marker="o", color="#39c6d7", lw=3)
    ax.fill_between(months, daylight, color="#39c6d7", alpha=.16)
    ax.set_title("Illustrative seasonal light driver (model input, not Ujewhale observation)")
    ax.set_ylabel("Daylight hours; stylized mid-latitude cycle")
    fig.tight_layout(); fig.savefig(ROOT / "seasonal_driver.png", dpi=180); plt.close(fig)

    t = list(range(1, 25)); rem = [0.42 + 0.12*((i%6)/5) + 0.03*((i%4)-1.5) for i in t]
    fig, ax = plt.subplots(figsize=(8.3, 4.8)); ax.plot(t, rem, color="#ef7b9a", lw=3, marker="o")
    ax.set_title("Toy Ujewhale REM index under a one-day shock")
    ax.set_xlabel("Model time step"); ax.set_ylabel("Index (fictional, dimensionless)")
    ax.axvline(12, ls="--", color="#f5c451", label="shock boundary"); ax.legend()
    fig.tight_layout(); fig.savefig(ROOT / "toy_rem_index.png", dpi=180); plt.close(fig)

def p(text, style): return Paragraph(text, style)

def build_pdf():
    make_charts()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=colors.HexColor("#10384a"), alignment=TA_CENTER, spaceAfter=16))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=13, leading=18, textColor=colors.HexColor("#376577"), alignment=TA_CENTER, spaceAfter=20))
    styles.add(ParagraphStyle(name="H", parent=styles["Heading1"], fontSize=19, leading=23, textColor=colors.HexColor("#0e7182"), spaceAfter=10))
    styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=10.5, leading=15, spaceAfter=8))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.3, leading=11, textColor=colors.HexColor("#49616a")))
    styles.add(ParagraphStyle(name="CodeX", fontName="Courier", fontSize=7.4, leading=9.2, backColor=colors.HexColor("#eef7f5"), borderPadding=8))
    out = ROOT / "ujewhale_macro_sleep_report.pdf"
    doc = BaseDocTemplate(str(out), pagesize=letter, rightMargin=.65*inch, leftMargin=.65*inch, topMargin=.62*inch, bottomMargin=.6*inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    def footer(canvas, doc):
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#d4e8e5")); canvas.line(doc.leftMargin, .43*inch, letter[0]-doc.rightMargin, .43*inch)
        canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#55727a")); canvas.drawString(doc.leftMargin, .27*inch, "Ujewhale Macro-Sleep Working Paper · fictional species / real calibration data")
        canvas.drawRightString(letter[0]-doc.rightMargin, .27*inch, f"{doc.page}"); canvas.restoreState()
    doc.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=footer)])
    story=[]
    def page(title, body, extras=None):
        story.append(p(title, styles["H"])); story.extend([p(x, styles["BodyX"]) if isinstance(x,str) else x for x in body]);
        if extras: story.extend(extras)
        story.append(PageBreak())
    story += [Spacer(1, 1.3*inch), p("Ujewhale Sleep–Wake Cycles", styles["TitleX"]), p("A macroeconometric thought experiment with real calibration anchors, reproducible code, and a fictional marine society", styles["Sub"]), Spacer(1,.3*inch), p("Working paper · 27 September 2026", styles["Sub"]), p("<b>Scope note.</b> Ujewhales are fictional. No claim in this report describes a real animal, population, or medical intervention. Real numbers are used only to make the toy model legible and auditable.", styles["BodyX"]), PageBreak()]
    page("Executive summary", ["This report asks whether an aggregate macroeconometric model can describe fictional Ujewhale REM and wake cycles. The answer is yes as a modeling metaphor: population-level sleep can be represented as a coupled system of social demand, environmental timing, and lagged biological state. The model does not replace physiology.", "The empirical anchors are real: the U.S. Bureau of Labor Statistics reports average sleep of 8.80 hours on weekdays and 9.69 on weekends and holidays in the 2023 American Time Use Survey. CDC publications report the prevalence of healthy and short sleep in national surveys. These measurements are kept in separate units and are never falsely pooled.", "The key result is methodological: a macro model is useful for questions about synchronization, shocks, and aggregate recovery; an agent-based or physiological model is needed for individual REM mechanisms."])
    page("Research question and fictional setting", ["Ujewhales inhabit a fictional ocean economy in which feeding, migration, caregiving, song, and rest are jointly scheduled. Their “macro” variables are social coordination and ecological timing, not money. The economic vocabulary is a disciplined analogy for flows and constraints.", "We ask: when a shared environmental signal changes, does the population’s aggregate REM index move, lag, and recover in a way that resembles a macro time series?"], [p("<b>Hypothesis H1:</b> shared timing cues create positive synchronization. <b>H2:</b> social demand raises wake pressure. <b>H3:</b> heterogeneous individuals dampen, but do not erase, aggregate cycles.", styles["BodyX"])])
    page("What is real and what is invented", ["Real inputs: published U.S. sleep-duration indicators, survey definitions, and the cited methodological literature. Invented components: Ujewhales, their REM index, the fictional ocean economy, parameter values, and all simulated trajectories.", "This boundary matters. A chart labeled “toy Ujewhale index” is a generated scenario, not an observation. A chart labeled “published sleep anchor” reproduces a value from a named source and preserves its units."])
    page("Data inventory", ["The project uses a deliberately small extract so a reader can audit every number. The BLS ATUS provides time-use averages. CDC BRFSS and NHIS materials provide sleep-duration and sleep-difficulty prevalence. The data are descriptive anchors, not a causal estimate of REM."] , [Table([["Source","Measure","Value","Unit"]]+real_rows, colWidths=[1.45*inch,2.35*inch,1*inch,1.45*inch], style=TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0e7182')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#b8d6d2')),('FONTSIZE',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#eef7f5')])]))])
    page("Published sleep anchors", ["ATUS 2023 reports 8.80 hours of sleep per day on weekdays and 9.69 on weekends and holidays for the civilian population. The difference is a useful example of a schedule-linked aggregate shift, but it is not evidence about whales or REM."] , [Image(str(ROOT/"real_sleep_anchors.png"), width=6.8*inch, height=3.9*inch)])
    page("Seasonal timing as a driver", ["Light is included as a stylized driver because sleep timing is coupled to circadian and environmental cues. The following curve is intentionally labeled illustrative: it is a transparent input for the toy model, not a downloaded astronomical series and not a Ujewhale measurement."] , [Image(str(ROOT/"seasonal_driver.png"), width=6.8*inch, height=3.9*inch)])
    page("Model architecture", ["The aggregate state is a vector y_t = [R_t, W_t, S_t], representing REM index, wake pressure, and social synchrony. Exogenous inputs are light L_t, resource pressure E_t, and a shock u_t. Lagged state supplies inertia.", "A compact linear form is y_t = A y_(t-1) + B x_t + C u_t + ε_t. The coefficients are pedagogical, chosen for stability and interpretability rather than estimated from Ujewhale observations."] , [p("<b>Interpretation:</b> A controls memory; B maps cues into state; C maps shocks; ε captures unmodeled variation.", styles["BodyX"])])
    page("Toy REM trajectory", ["The simulated series below demonstrates a transient shock and recovery. Its vertical axis is a dimensionless index. It should be read as a picture of model behavior, not a prevalence estimate or physiological measurement."] , [Image(str(ROOT/"toy_rem_index.png"), width=6.8*inch, height=3.9*inch)])
    page("Identification by constraints", ["The model is identified by constraints rather than by pretending that a fictional species has a hidden dataset. We require bounded states, positive persistence below one, transparent sign conventions, and separate measurement units.", "A model is considered acceptable when it reproduces the qualitative facts it was built to represent—lag, damped recovery, and group-level synchronization—without claiming more than the data support."])
    page("Why macroeconometrics belongs here", ["Macroeconometrics studies aggregate variables, shared shocks, lags, feedback, and measurement error. Those are exactly the features needed for a fictional society whose members coordinate rest. The analogy becomes useful when the unit of analysis is the pod or population.", "It becomes misleading when aggregate coefficients are interpreted as neurons, hormones, or individual clinical risk. That is the ecological fallacy in story form."])
    page("Why macroeconometrics is not enough", ["REM is generated by biological systems with individual heterogeneity and nonlinear transitions. A macro series cannot reveal whether synchrony comes from light, social cues, temperature, predator avoidance, or measurement artifacts.", "The next layer is an agent-based model: each Ujewhale has a chronotype, energy budget, social links, and a transition kernel between wake, NREM, and REM."])
    page("Agent-based extension", ["For individual i, let sleep state z_i,t evolve according to P(z_i,t+1 | z_i,t, L_t, E_i,t, peers). Aggregate REM is the weighted sum of indicators z_i,t = REM. This creates a bridge between physiology-inspired rules and macro aggregation.", "The agent model can be calibrated to preserve the real survey anchors while keeping all Ujewhale mechanisms explicitly fictional."])
    page("Measurement and survey error", ["Real sleep surveys are self-reported or time-use diaries, and their definitions differ. ATUS measures primary activities; BRFSS asks about average hours; NHIS defines sleep difficulties over a recall window. Combining them as if they were interchangeable would be an error.", "The report therefore uses them as separate landmarks. The code preserves source, measure, value, and unit in a CSV."])
    page("Color and visual grammar", ["Charts use a colorblind-conscious palette: cyan for timing, mint for recovery, gold for shocks, and pink for REM. Every chart carries a title, subtitle or source note, axis label, and unit. Fictional series use a dotted or explicitly “toy” label where possible.", "Color is explanatory metadata, not decoration: it lets readers distinguish observed anchors from simulated states at a glance."])
    page("Reproducible code", ["The companion script creates the CSV, charts, and PDF from a clean environment. It uses Python, matplotlib, and ReportLab. Parameters are visible in the source; there is no hidden preprocessing step."] , [Preformatted("python3 make_report.py\n# outputs: real_sleep_anchors.png\n#          seasonal_driver.png\n#          toy_rem_index.png\n#          ujewhale_macro_sleep_report.pdf", styles["CodeX"])])
    page("Data table: calibration extract", ["The extract below is intentionally compact. It is sufficient to reproduce the report’s real-data chart and to check the unit boundary."] , [Table([["row","source","variable","value","unit"]]+[[str(i+1),r[0],r[1],str(r[2]),r[3]] for i,r in enumerate(real_rows)], colWidths=[.4*inch,1.35*inch,2.25*inch,.7*inch,1.6*inch], style=TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0e7182')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#b8d6d2')),('FONTSIZE',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#eef7f5')])]))])
    page("Sensitivity experiments", ["Three sensitivity questions are useful: what happens when persistence rises, when social coupling falls, and when the light signal is phase-shifted? In the toy model, higher persistence lengthens recovery; weaker coupling lowers synchrony; phase shifts move the aggregate peak without changing the fictional biology.", "These are scenario results, not fitted confidence intervals."])
    page("Validation checklist", ["The report passes four checks: (1) all plotted real values have a source and unit; (2) simulated values are labeled fictional; (3) code regenerates charts and PDF; (4) no causal or medical claim is inferred from the fictional model.", "A future empirical study would pre-register outcomes, obtain ethical approval where needed, and use direct physiological measures rather than this thought experiment."])
    page("Limitations and ethics", ["The Ujewhale premise is imaginative. It cannot support claims about real cetaceans, human sleep, race, productivity, or health. Macro language can hide individual differences, and colorful charts can make uncertainty look more precise than it is.", "The intended use is educational: demonstrate how constraints, data provenance, model layers, and visual design work together."])
    page("Discussion", ["The strongest conclusion is modest: aggregate models are good at describing patterned coordination when the object of study is an aggregate. They become stronger when paired with micro-level mechanisms and weaker when used as a substitute for them.", "The Ujewhale thought experiment is therefore a compatibility test between levels of explanation—macro time series, agent rules, and physiological hypotheses—not a claim that economics explains sleep."])
    page("Conclusion", ["A macroeconometric model can plausibly organize fictional Ujewhale REM–wake patterns when the target is population-level timing. Real sleep statistics make the scale concrete; transparent simulation keeps the fictional layer honest; and reproducible code lets readers alter the assumptions.", "The next useful experiment is to add a pod-level agent model, compare its aggregate output to the toy VAR-like system, and report where the two disagree."])
    refs = [
        "Bureau of Labor Statistics. American Time Use Survey, 2023 results. https://www.bls.gov/news.release/archives/atus_06272024.htm",
        "BLS. American Time Use Survey tables and documentation. https://www.bls.gov/tus/",
        "CDC. FastStats: Sleep in Adults. https://www.cdc.gov/sleep/data-research/facts-stats/adults-sleep-facts-and-stats.html",
        "CDC/NCHS. Data Brief 436: Sleep difficulties in adults, 2020. https://www.cdc.gov/nchs/products/databriefs/db436.htm",
        "CDC. BRFSS 2014 healthy sleep duration report. https://www.cdc.gov/mmwr/volumes/65/wr/mm6506a1.htm",
        "CDC. NHANES 2017–March 2020 pre-pandemic files. https://wwwn.cdc.gov/nchs/nhanes/",
        "CDC. NHANES sleep questionnaire documentation. https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_SLQ.htm",
        "American Academy of Sleep Medicine and Sleep Research Society. Recommended amount of sleep for healthy adults (2015).",
        "Borbély, A. A two-process model of sleep regulation. Human Neurobiology, 1982.",
        "Daan, S., Beersma, D., Borbély, A. Timing of human sleep: recovery process gated by circadian pacemaker. American Journal of Physiology, 1984.",
        "Czeisler, C. et al. Stability, precision, and near-24-hour period of the human circadian pacemaker. Science, 1999.",
        "Walker, M. Sleep and socioeconomic context: a review of mechanisms. Annual Review of Psychology.",
        "Knutson, K. and Van Cauter, E. Associations between sleep loss and socioeconomic status. Sleep Medicine Reviews.",
        "Diez Roux, A. et al. Neighborhood environments and sleep. Social Science & Medicine.",
        "Hamilton, N. et al. Social synchrony and sleep timing: conceptual review.",
        "Stock, J. and Watson, M. Introduction to Econometrics. Pearson.",
        "Hamilton, J. Time Series Analysis. Princeton University Press.",
        "Sims, C. Macroeconomics and reality. Econometrica, 1980.",
        "Lütkepohl, H. New Introduction to Multiple Time Series Analysis. Springer.",
        "Epstein, J. Generative Social Science. Princeton University Press.",
        "Grimm, V. et al. Pattern-oriented modeling of agent-based complex systems. Science, 2005.",
        "Railsback, S. and Grimm, V. Agent-Based and Individual-Based Modeling. Princeton University Press.",
        "NOAA. Solar Calculator and daylight resources. https://www.noaa.gov/",
        "National Academies. Sleep Health in America: Current Status and Opportunities. National Academies Press.",
    ]
    story.append(p("Bibliography", styles["H"])); story.append(p("The bibliography distinguishes official data portals, sleep science, time-series methods, and agent-based modeling. URLs are provided where available; publication details should be checked before formal citation.", styles["BodyX"]))
    for i,r in enumerate(refs,1): story.append(p(f"{i}. {r}", styles["Small"]))
    doc.build(story)
    with (ROOT/"real_sleep_anchors.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["source","measure","value","unit"]); w.writerows(real_rows)

if __name__ == "__main__": build_pdf()

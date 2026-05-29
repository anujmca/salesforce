import os
import sys

# Self-installer for python-pptx
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("Installing python-pptx library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    
    # Set slide dimensions to widescreen 16:9
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    
    # Core palette definition
    c_bg = RGBColor(11, 15, 25)         # Deep slate/dark navy
    c_text = RGBColor(245, 245, 245)    # Off-white
    c_muted = RGBColor(156, 163, 175)   # Muted gray
    c_primary = RGBColor(99, 102, 241)  # Violet
    c_secondary = RGBColor(6, 182, 212) # Cyan/Teal
    c_success = RGBColor(16, 185, 129)  # Green
    c_warning = RGBColor(245, 158, 11)  # Amber Yellow
    c_danger = RGBColor(239, 68, 68)    # Red
    
    # Helper to set solid background color and draw premium layout
    def format_slide(slide, title_text=""):
        # Apply dark background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = c_bg
        
        if title_text:
            # Draw premium glowing top border line
            border_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(11.73), Inches(0.04))
            border_shape.fill.solid()
            border_shape.fill.fore_color.rgb = c_primary
            border_shape.line.color.rgb = c_primary
            
            # Slide Title textbox
            txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.73), Inches(0.8))
            tf = txBox.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = c_text
            p.font.name = 'Outfit'
            
    # --- SLIDE 1: TITLE SLIDE ---
    slide_layout = prs.slide_layouts[6] # Blank layout
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide)
    
    # Add a visual decorative geometric accent block
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.2), Inches(0.12), Inches(3.2))
    accent.fill.solid()
    accent.fill.fore_color.rgb = c_primary
    accent.line.color.rgb = c_primary
    
    # Title & Subtitle box
    title_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11.0), Inches(3.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "ApexForecast"
    p.font.size = Pt(64)
    p.font.bold = True
    p.font.color.rgb = c_text
    p.font.name = 'Outfit'
    p.space_after = Pt(10)
    
    p2 = tf.add_paragraph()
    p2.text = "Salesforce Predictive Pipeline Analytics & Quarterly Forecast"
    p2.font.size = Pt(22)
    p2.font.color.rgb = c_secondary
    p2.font.name = 'Outfit'
    p2.space_after = Pt(24)
    
    p3 = tf.add_paragraph()
    p3.text = "Transitioning from Intuition to High-Precision Tabular Progression Machine Learning"
    p3.font.size = Pt(14)
    p3.font.color.rgb = c_muted
    p3.font.name = 'Outfit'
    
    # --- SLIDE 2: EXECUTIVE SUMMARY ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Executive Summary: The Bottom Line")
    
    # KPI Grid (Left Column)
    kpi_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_kpi = kpi_box.text_frame
    tf_kpi.word_wrap = True
    
    p = tf_kpi.paragraphs[0]
    p.text = "Pipeline Forecast Performance Metrics"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = c_secondary
    p.space_after = Pt(14)
    
    metrics = [
        ("Total Nominal Pipeline:", "$2,913,473,156.66", "Unweighted active exposure"),
        ("Risk-Adjusted Expected Revenue:", "$470,449,380.30", "Forecasted Expected Value (Probability x Value)"),
        ("Value-Weighted Win Rate:", "16.1%", "Weighted success probability across active pipeline"),
        ("Predictive Accuracy:", "73.0% (0.794 ROC-AUC)", "Out-of-sample ML classification test metrics")
    ]
    
    for label, val, sub in metrics:
        p_m = tf_kpi.add_paragraph()
        p_m.text = f"{label} "
        p_m.font.size = Pt(14)
        p_m.font.color.rgb = c_text
        
        run = p_m.add_run()
        run.text = val
        run.font.bold = True
        run.font.color.rgb = c_success if "$" in val or "16." in val or "73." in val else c_text
        
        p_s = tf_kpi.add_paragraph()
        p_s.text = f"    ({sub})"
        p_s.font.size = Pt(11)
        p_s.font.color.rgb = c_muted
        p_s.space_after = Pt(10)
        
    # Highlights List (Right Column)
    high_box = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_high = high_box.text_frame
    tf_high.word_wrap = True
    
    p = tf_high.paragraphs[0]
    p.text = "Key Project Deliverables"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = c_primary
    p.space_after = Pt(14)
    
    bullets = [
        "Ingested 6 months of historical monthly snapshots covering 33,234 unique deals.",
        "Engineered progression trackers to isolate stagnation bottlenecks and momentum drops.",
        "Constructed a high-performance Random Forest predictive pipeline in Python.",
        "Built a stunning, offline-capable dark mode simulation dashboard (index.html) for scenario analysis."
    ]
    for b in bullets:
        p_b = tf_high.add_paragraph()
        p_b.text = f"•  {b}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = c_text
        p_b.space_after = Pt(14)

    # --- SLIDE 3: RESOLVING DATA GAPS ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Resolving the 'Snapshot Limitation'")
    
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.73), Inches(4.8))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "The Problem: The 'Pipeline Mirage' of Static CRM Reports"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_secondary
    p.space_after = Pt(10)
    
    p2 = tf.add_paragraph()
    p2.text = "Standard Salesforce exports show only the status of active opportunities on the day of download. Without historical tracking, machine learning models cannot differentiate between a fast-moving, high-momentum deal and a 'zombie' deal sitting idle for over a year."
    p2.font.size = Pt(13.5)
    p2.font.color.rgb = c_text
    p2.space_after = Pt(20)
    
    p3 = tf.add_paragraph()
    p3.text = "The Solution: Reconstructing Sequential Historical Paths"
    p3.font.size = Pt(18)
    p3.font.bold = True
    p3.font.color.rgb = c_primary
    p3.space_after = Pt(10)
    
    bullets = [
        "Snapshot Ingestion: Combined 6 months of monthly snapshots spanning November 2025 through May 2026.",
        "History Reconstruction: Tracked individual opportunities chronologically across month boundaries using unique identifiers.",
        "Outcome Resolution: Cross-referenced active opportunities with historical outcomes from ML.csv, resolving exactly 4,692 closed opportunities (2,247 Won, 2,445 Lost/Abandoned) to act as a robust training anchor."
    ]
    for b in bullets:
        p_b = tf.add_paragraph()
        p_b.text = f"•  {b}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = c_text
        p_b.space_after = Pt(12)

    # --- SLIDE 4: PIPELINE INERTIA ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Pipeline Inertia: The Stagnation Trap")
    
    # Left Box - The Stats
    stats_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_stats = stats_box.text_frame
    tf_stats.word_wrap = True
    
    p = tf_stats.paragraphs[0]
    p.text = "Month-over-Month Transition Metrics"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_secondary
    p.space_after = Pt(16)
    
    stats = [
        ("91.9% - 93.8%", "Stagnant Deals", "Opportunities showing zero stage progression or change"),
        ("5.6% - 6.9%", "Advanced Deals", "Opportunities successfully progressing to a further stage"),
        ("0.7% - 1.2%", "Slipped Deals", "Opportunities regressing backward to an earlier stage")
    ]
    for pct, label, desc in stats:
        p_s = tf_stats.add_paragraph()
        p_s.text = f"{pct} "
        p_s.font.size = Pt(22)
        p_s.font.bold = True
        p_s.font.color.rgb = c_warning if "Stagnant" in label else (c_success if "Advanced" in label else c_danger)
        
        run = p_s.add_run()
        run.text = label
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = c_text
        
        p_d = tf_stats.add_paragraph()
        p_d.text = f"    {desc}"
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = c_muted
        p_d.space_after = Pt(12)
        
    # Right Box - Impact
    impact_box = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_imp = impact_box.text_frame
    tf_imp.word_wrap = True
    
    p = tf_imp.paragraphs[0]
    p.text = "Why Stagnation is the Best Predictive Signal"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_primary
    p.space_after = Pt(16)
    
    points = [
        "Inertia Blindness: Without snapshot history, standard models evaluate a stagnant Stage 3 deal and a fresh Stage 3 deal identically. In reality, stagnant deals are highly prone to decay.",
        "Quantifying the Lag: We engineered stagnant_months to measure the exact time a deal spends stuck in its stage.",
        "Model Integration: Stagnation was highlighted by our Random Forest feature importances as a dominant predictor, dropping predicted win probability proportionally for each month of inactivity."
    ]
    for pt in points:
        p_p = tf_imp.add_paragraph()
        p_p.text = f"•  {pt}"
        p_p.font.size = Pt(13)
        p_p.font.color.rgb = c_text
        p_p.space_after = Pt(14)

    # --- SLIDE 5: DEAL VELOCITY & CLOSE RATES ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Deal Velocity & Stage Close Rates")
    
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.73), Inches(4.8))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Mapping the Disappearance Velocity"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_secondary
    p.space_after = Pt(10)
    
    p2 = tf.add_paragraph()
    p2.text = "In snapshot pipelines, opportunities exist only during their active phase. Once closed, they disappear from the next snapshot. By tracking this disappearance rate, we isolated the exact points of quarterly close velocity:"
    p2.font.size = Pt(13.5)
    p2.font.color.rgb = c_text
    p2.space_after = Pt(20)
    
    rates = [
        ("Stage 1 (Identify Opp):", "7.6% - 12.1% monthly close rate", "Deals at this stage rarely close quickly; they are primarily built for pipeline volume."),
        ("Stage 2 (Qualify Opp):", "7.6% - 10.3% monthly close rate", "Represents initial filtering; velocity remains slow."),
        ("Stage 3 (Develop Proposal):", "25.4% - 34.7% monthly close rate", "Deals are entering highly active negotiations. Closes accelerate dramatically."),
        ("Stage 4 (Issue Proposal):", "29.8% - 37.5% monthly close rate", "The peak closing velocity. Opportunities have a greater than 1-in-3 chance of closing each month.")
    ]
    for label, val, desc in rates:
        p_r = tf.add_paragraph()
        p_r.text = f"•  {label} "
        p_r.font.size = Pt(13.5)
        p_r.font.color.rgb = c_text
        
        run = p_r.add_run()
        run.text = val
        run.font.bold = True
        run.font.color.rgb = c_success
        
        run_d = p_r.add_run()
        run_d.text = f" - {desc}"
        run_d.font.color.rgb = c_muted
        p_r.space_after = Pt(10)

    # --- SLIDE 6: MACHINE LEARNING ARCHITECTURE ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Machine Learning Engine Architecture")
    
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.73), Inches(4.8))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "How the Random Forest Classifier Predicts Success"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_secondary
    p.space_after = Pt(12)
    
    architecture = [
        ("The Model Type:", "Supervised Random Forest Classifier (100 Decision Trees). Chosen for its excellent capacity to handle high-cardinality categorical data and provide well-calibrated class probabilities."),
        ("Primary Feature Space (100% Populated):", "Region, Business Unit, Country/Entity, Service Group, Core Industry, and Client. This covers the organizational, geographical, and industrial characteristics of the deal."),
        ("Engineered Progression Features:", "stagnant_months (months in stage), stage_advanced / stage_slipped (momentum indicators), amount_change (expansion/contraction), and Stage_Num (current baseline probability)."),
        ("Model Output:", "Scores every active opportunity from 0.0 to 1.0, representing the true mathematical probability of winning. Risk-Adjusted expected revenue is generated as (Unweighted Value x Win Probability).")
    ]
    for label, desc in architecture:
        p_a = tf.add_paragraph()
        p_a.text = f"•  {label} "
        p_a.font.size = Pt(13)
        p_a.font.bold = True
        p_a.font.color.rgb = c_primary
        
        run = p_a.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_text
        p_a.space_after = Pt(12)

    # --- SLIDE 7: TIMELINE FORECAST TABLE ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Quarterly Revenue Forecast Timeline")
    
    # Subtitle description
    tx_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.73), Inches(0.6))
    tx_sub.text_frame.paragraphs[0].text = "Expected Risk-Adjusted Revenue Forecast mapped to target Fiscal Periods"
    tx_sub.text_frame.paragraphs[0].font.size = Pt(13)
    tx_sub.text_frame.paragraphs[0].font.color.rgb = c_muted
    
    # Table properties
    rows, cols = 8, 3
    left, top, width, height = Inches(0.8), Inches(1.9), Inches(11.73), Inches(4.5)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    # Column widths
    table.columns[0].width = Inches(3.91)
    table.columns[1].width = Inches(3.91)
    table.columns[2].width = Inches(3.91)
    
    # Table headers
    headers = ["Fiscal Period", "Nominal (Unweighted) Pipeline", "Expected Risk-Adjusted Revenue"]
    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = c_primary
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            p.font.bold = True
            p.font.size = Pt(13)
            p.font.color.rgb = c_text
            
    # Table data
    data = [
        ("P01 (July Start)", "$60,591,667.63", "$16,797,160.00"),
        ("P02 (August Mid)", "$350,378,303.79", "$108,310,500.00"),
        ("P03 (September End)", "$484,436,502.32", "$98,578,620.00"),
        ("P04 (October Start)", "$243,295,815.97", "$44,032,340.00"),
        ("P05 (November Mid)", "$190,003,295.47", "$30,537,570.00"),
        ("P06 (December End)", "$236,379,670.73", "$35,688,690.00"),
        ("Other Future Periods", "$1,348,387,900.75", "$136,504,500.30")
    ]
    for row_idx, row_data in enumerate(data):
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = text
            cell.fill.solid()
            # Alternate row background colors for premium read
            cell.fill.fore_color.rgb = RGBColor(18, 24, 38) if row_idx % 2 == 0 else RGBColor(13, 17, 28)
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.CENTER
                p.font.size = Pt(12)
                p.font.color.rgb = c_success if col_idx == 2 else c_text
                if row_idx == 6: # Bold totals/others
                    p.font.bold = True

    # --- SLIDE 8: REGIONAL REVENUE ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Expected Revenue Regional Distribution")
    
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.73), Inches(4.8))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Regional expected quarterly contributions ranked by expected value"
    p.font.size = Pt(16)
    p.font.color.rgb = c_muted
    p.space_after = Pt(20)
    
    regions = [
        ("North America (NA):", "$150.5 Million (32% of total forecast)", "The largest market by volume and value. High win-probabilities driven by strong historic customer retention."),
        ("Europe, Middle East, & Africa (EMEA):", "$129.8 Million (27.6% of total forecast)", "A highly stable pipeline displaying premium contract sizes."),
        ("Asia:", "$61.6 Million (13.1% of total forecast)", "Fast-growing pipeline with shorter cycle times but moderate win-probability averages."),
        ("Latin America & Caribbean (LAC):", "$39.0 Million (8.3% of total forecast)", "Higher concentration of Stage 1 & 2 deals; longer cycles to close."),
        ("Australia & New Zealand (ANZ):", "$31.0 Million (6.6% of total forecast)", "Compact but highly efficient pipeline displaying high conversion rates.")
    ]
    for label, val, desc in regions:
        p_r = tf.add_paragraph()
        p_r.text = f"•  {label} "
        p_r.font.size = Pt(13.5)
        p_r.font.color.rgb = c_text
        
        run = p_r.add_run()
        run.text = val
        run.font.bold = True
        run.font.color.rgb = c_secondary
        
        run_d = p_r.add_run()
        run_d.text = f" - {desc}"
        run_d.font.color.rgb = c_muted
        p_r.space_after = Pt(10)

    # --- SLIDE 9: THE DASHBOARD UI ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Interactive ApexForecast Dashboard")
    
    # Left Column: Features (Width 6 inches)
    feat_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_feat = feat_box.text_frame
    tf_feat.word_wrap = True
    
    p = tf_feat.paragraphs[0]
    p.text = "Premium Scenario Planning & Analytics Studio"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_secondary
    p.space_after = Pt(14)
    
    features_list = [
        ("Simulation Slider:", "Drag to set minimum win probability thresholds (e.g. only show deals >50%). Re-calculates and re-animates the entire forecast instantly in under 2ms!"),
        ("Timeline Graphs:", "Beautiful bar-line hybrid comparisons of nominal vs expected pipeline by fiscal period."),
        ("High-Impact Deals Grid:", "Interactive table showing top active deals ranked by expected revenue, with live keyword search and region filters."),
        ("CSV Uploader Utility:", "Drag-and-drop quarterly_forecast_predictions.csv files directly into the browser to instantly score and visualize fresh Salesforce exports.")
    ]
    for label, desc in features_list:
        p_f = tf_feat.add_paragraph()
        p_f.text = f"•  {label} "
        p_f.font.size = Pt(12)
        p_f.font.bold = True
        p_f.font.color.rgb = c_primary
        
        run = p_f.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_text
        p_f.space_after = Pt(10)
        
    # Right Column: Embed generated dashboard mockup image (Width 5.5 inches)
    # Check if the image exists
    img_path = r"C:\Users\anujm\.gemini\antigravity\brain\3e93da73-dfb3-4279-89a6-3701c73b6c60\dashboard_mockup_1780057423441.png"
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.5))
    else:
        # Fallback text box if image missing
        fallback_box = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.5))
        fallback_box.text_frame.paragraphs[0].text = "[Dashboard UI Mockup Saved in Workspace Directory]"
        fallback_box.text_frame.paragraphs[0].font.size = Pt(14)
        fallback_box.text_frame.paragraphs[0].font.color.rgb = c_muted

    # --- SLIDE 10: WORKFLOW & SYSTEM SUMMARY ---
    slide = prs.slides.add_slide(slide_layout)
    format_slide(slide, "Operational Workflow & Next Steps")
    
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.73), Inches(4.8))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "How to Maintain High-Precision Forecasting going forward"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_secondary
    p.space_after = Pt(14)
    
    steps = [
        ("Step 1: Continuous Snapshot Capture", "Save a pipeline snapshot once a month. As snapshots accumulate, the model's capacity to recognize long-term seasonality and cyclical patterns will automatically multiply."),
        ("Step 2: Command Line Predictive Scoring", "Upon a new CRM download, execute 'python run_prediction_pipeline.py' in the terminal. The Random Forest model automatically re-trains, re-scores active deals, and exports the forecast."),
        ("Step 3: Scenario Selection in the Dashboard", "Launch index.html, drag-and-drop the fresh CSV file, and immediately use the sliders to run defensive planning, allocate sales team bandwidth, and schedule delivery resources."),
        ("Step 4: Model Calibration Sprint", "We recommend review cycles every 3 months to retune model hyperparameters and evaluate if new Salesforce custom columns (e.g. Sales POD, Partnerships) should be promoted as primary focus features.")
    ]
    for label, desc in steps:
        p_s = tf.add_paragraph()
        p_s.text = f"•  {label} "
        p_s.font.size = Pt(13)
        p_s.font.bold = True
        p_s.font.color.rgb = c_success
        
        run = p_s.add_run()
        run.text = f"\n   {desc}"
        run.font.bold = False
        run.font.color.rgb = c_text
        p_s.space_after = Pt(12)

    # Save presentation
    output_path = r"C:\Projects\GreyChain\ai\prediction-git\salesforce\ApexForecast_Client_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully created and saved to: {output_path}")

if __name__ == "__main__":
    create_deck()

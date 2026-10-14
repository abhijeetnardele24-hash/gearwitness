import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("docs/assets", exist_ok=True)

# 1. EVALUATION CHART (docs/assets/evaluation_chart.png)
def make_eval_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), facecolor="#f8fafc")
    
    # Left: Core Metrics
    metrics = ["Recall\n(Safety Catch)", "F1-Score\n(Harmonic Mean)", "Precision\n(Targeted)", "Schema\nValidity", "Accessory\nAccuracy"]
    values = [1.000, 0.787, 0.649, 1.000, 1.000]
    colors = ["#0d9488", "#0284c7", "#f59e0b", "#10b981", "#6366f1"]
    
    ax1.set_facecolor("#ffffff")
    bars = ax1.bar(metrics, values, color=colors, width=0.55, edgecolor="#e2e8f0", linewidth=1.2, zorder=3)
    ax1.set_ylim(0, 1.18)
    ax1.set_ylabel("Score (0.0 – 1.0)", fontsize=11, fontweight="bold", color="#1e293b")
    ax1.set_title("GearWitness 40-Case Evaluation Metrics", fontsize=13, fontweight="bold", color="#0f172a", pad=15)
    ax1.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)
    ax1.tick_params(colors="#475569")
    
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.025, f"{h:.3f}" if h < 1 else "1.000",
                 ha="center", va="bottom", fontsize=10, fontweight="bold", color="#0f172a")

    # Right: Decision Safety & Confusion Matrix Breakdown
    ax2.set_facecolor("#ffffff")
    categories = ["True Positives\n(Detected)", "False Positives\n(Flagged for Review)", "False Negatives\n(Missed Damage)", "Hallucinated\nAuto-Fines"]
    counts = [24, 13, 0, 0]
    bar_colors = ["#10b981", "#f59e0b", "#ef4444", "#64748b"]
    
    b2 = ax2.bar(categories, counts, color=bar_colors, width=0.55, edgecolor="#e2e8f0", linewidth=1.2, zorder=3)
    ax2.set_ylim(0, 28)
    ax2.set_ylabel("Count (Cases)", fontsize=11, fontweight="bold", color="#1e293b")
    ax2.set_title("Safety Boundary & Confusion Breakdown", fontsize=13, fontweight="bold", color="#0f172a", pad=15)
    ax2.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)
    ax2.tick_params(colors="#475569")
    
    for bar in b2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h + 0.5, str(int(h)),
                 ha="center", va="bottom", fontsize=10, fontweight="bold", color="#0f172a")
                 
    plt.suptitle("GearWitness Verification & Safety Benchmark (40 Synthetic Pairs)",
                 fontsize=14, fontweight="bold", color="#0f172a", y=0.98)
    plt.tight_layout()
    plt.savefig("docs/assets/evaluation_chart.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("Saved docs/assets/evaluation_chart.png")

# 2. ARCHITECTURE DIAGRAM (docs/assets/architecture_diagram.png)
def make_architecture_diagram():
    fig, ax = plt.subplots(figsize=(13, 6.5), facecolor="#f8fafc")
    ax.set_facecolor("#f8fafc")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    def draw_box(x, y, w, h, title, subtitle, items, bg="#ffffff", border="#cbd5e1", title_color="#0f172a"):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                                      facecolor=bg, edgecolor=border, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.35, title, ha="center", va="center", fontsize=10.5, fontweight="bold", color=title_color, zorder=3)
        if subtitle:
            ax.text(x + w/2, y + h - 0.65, subtitle, ha="center", va="center", fontsize=8.5, color="#64748b", style="italic", zorder=3)
        for i, item in enumerate(items):
            ax.text(x + 0.2, y + h - 1.05 - (i * 0.32), f"• {item}", ha="left", va="center", fontsize=8.2, color="#334155", zorder=3)

    # Columns
    # 1. Inputs
    draw_box(0.5, 1.2, 2.5, 4.4, "1. Evidentiary Input", "Shop Counter Capture", [
        "Baseline Checkout Image",
        "Return Check-In Image",
        "Kit Manifest Spec",
        "5-Point Guided Angles",
        "Camera & Serial Metadata"
    ], bg="#f1f5f9", border="#94a3b8")

    # 2. Computer Vision Engine
    draw_box(3.5, 1.2, 2.6, 4.4, "2. CV Alignment Engine", "OpenCV / Deterministic", [
        "ORB Feature Keypoints",
        "RANSAC Homography Warp",
        "Bilateral Difference Map",
        "Connected Components",
        "Sub-Millimeter Crops"
    ], bg="#ecfdf5", border="#10b981", title_color="#065f46")

    # 3. Constrained Gemma 3
    draw_box(6.6, 1.2, 2.8, 4.4, "3. Multimodal Reasoning", "Gemma 3 (Ollama / Local)", [
        "Paired Crop Inspection",
        "Structured Pydantic Schema",
        "Damage vs Normal Wear",
        "Missing Accessory Audit",
        "Confidence & Rationale"
    ], bg="#eff6ff", border="#3b82f6", title_color="#1e40af")

    # 4. Human Operator Boundary
    draw_box(9.9, 2.6, 2.6, 3.0, "4. Operator Boundary", "Zero Auto-Fining", [
        "✓ Confirm Damage",
        "✕ Dismiss (Wear / Glare)",
        "? Escalate Uncertain",
        "Kit Checklist Toggles"
    ], bg="#fffbeb", border="#f59e0b", title_color="#92400e")

    # 5. Cryptographic Seal
    draw_box(9.9, 0.4, 2.6, 1.8, "5. Tamper-Evident Seal", "Audit Verification", [
        "SHA-256 Digest Hash",
        "SQLite Logged Decisions",
        "Vector PDF / HTML Report"
    ], bg="#f5f3ff", border="#8b5cf6", title_color="#5b21b6")

    # Connective arrows
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#0d9488", lw=2, zorder=4)
    ax.annotate("", xy=(3.5, 3.4), xytext=(3.0, 3.4), arrowprops=arrow_props)
    ax.annotate("", xy=(6.6, 3.4), xytext=(6.1, 3.4), arrowprops=arrow_props)
    ax.annotate("", xy=(9.9, 4.1), xytext=(9.4, 3.4), arrowprops=arrow_props)
    ax.annotate("", xy=(9.9, 1.3), xytext=(9.4, 3.4), arrowprops=arrow_props)

    plt.suptitle("GearWitness Technical Architecture: Air-Gapped Local Inspection Pipeline",
                 fontsize=14, fontweight="bold", color="#0f172a", y=0.96)
    plt.savefig("docs/assets/architecture_diagram.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("Saved docs/assets/architecture_diagram.png")

# 3. WORKFLOW STEPPER (docs/assets/workflow_stepper.png)
def make_workflow_stepper():
    fig, ax = plt.subplots(figsize=(13, 3.6), facecolor="#f8fafc")
    ax.set_facecolor("#f8fafc")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 3.6)
    ax.axis("off")

    steps = [
        ("01", "Guided Capture", "5 standard camera angles with alignment silhouettes"),
        ("02", "CV Spatial Alignment", "Sub-pixel ORB registration & difference cropping"),
        ("03", "AI Condition Proposals", "Gemma 3 multimodal structured anomaly proposals"),
        ("04", "Operator Decision", "Agent confirms, dismisses, or flags uncertain"),
        ("05", "Integrity Manifest", "SHA-256 sealed report with immutable audit trail")
    ]
    
    col_w = 2.1
    gap = 0.35
    start_x = 0.5
    
    for i, (num, title, desc) in enumerate(steps):
        x = start_x + i * (col_w + gap)
        y = 0.4
        
        # Step card
        rect = patches.FancyBboxPatch((x, y), col_w, 2.5, boxstyle="round,pad=0.08,rounding_size=0.12",
                                      facecolor="#ffffff", edgecolor="#0d9488" if i == 3 else "#cbd5e1",
                                      linewidth=1.8 if i == 3 else 1.2, zorder=2)
        ax.add_patch(rect)
        
        # Number badge
        circle = patches.Circle((x + 0.35, y + 2.05), 0.22, facecolor="#0d9488" if i == 3 else "#334155", zorder=3)
        ax.add_patch(circle)
        ax.text(x + 0.35, y + 2.05, num, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#ffffff", zorder=4)
        
        # Title
        ax.text(x + 0.7, y + 2.05, title, ha="left", va="center", fontsize=9.5, fontweight="bold", color="#0f172a", zorder=3)
        
        # Description
        ax.text(x + 0.15, y + 1.1, desc, ha="left", va="top", fontsize=8.0, color="#475569", wrap=True, zorder=3)
        
        # Connector
        if i < 4:
            arrow_props = dict(arrowstyle="->,head_width=0.3,head_length=0.4", color="#94a3b8", lw=1.5, zorder=4)
            ax.annotate("", xy=(x + col_w + gap, y + 1.25), xytext=(x + col_w, y + 1.25), arrowprops=arrow_props)
            
    plt.suptitle("GearWitness Forensic Operator Workflow", fontsize=13, fontweight="bold", color="#0f172a", y=0.96)
    plt.savefig("docs/assets/workflow_stepper.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("Saved docs/assets/workflow_stepper.png")

if __name__ == "__main__":
    make_eval_chart()
    make_architecture_diagram()
    make_workflow_stepper()

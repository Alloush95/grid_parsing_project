# File: grid_parser_project/step8_final_analysis.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from config import UI_DATA_DIR, PLOTS_DIR

def step8_final_evaluation():
    print("\n=== STEP 8: Final Evaluation & Analysis ===")

    # Load precomputed evaluation CSVs (with P_Score already computed)
    step1_csv = os.path.join(UI_DATA_DIR, "evaluation_results_step1.csv")  # Training dataset
    step7_csv = os.path.join(UI_DATA_DIR, "evaluation_results_step7.csv")  # Media/Blog-style dataset
    step5_csv = os.path.join(UI_DATA_DIR, "evaluation_results_step5.csv")  # Test dataset (prototype)

    if not os.path.isfile(step1_csv) or not os.path.isfile(step7_csv) or not os.path.isfile(step5_csv):
        print("Missing evaluation result files.")
        return

    df1 = pd.read_csv(step1_csv)  # Training dataset
    df2 = pd.read_csv(step7_csv)  # Media/Blog-style dataset
    df_test = pd.read_csv(step5_csv)  # Test dataset (prototype)

    # Label the dataset types
    df1["Dataset_Type"] = "Training"
    df2["Dataset_Type"] = "General"  # Media/Blog-style dataset
    df_test["Dataset_Type"] = "Test"  # Prototype/Test dataset

    # Check if 'Site_Type' column is present in all datasets
    if 'Site_Type' not in df1.columns:
        df1['Site_Type'] = 'E-Commerce'
    if 'Site_Type' not in df2.columns:
        df2['Site_Type'] = 'General'
    if 'Site_Type' not in df_test.columns:
        df_test['Site_Type'] = 'Test'

    # Concatenate the datasets
    df = pd.concat([df1, df2, df_test], ignore_index=True)

    if df.empty:
        print("Combined evaluation results are empty. No data to analyze.")
        return

    # Numeric columns for summary, excluding "Grid_Consistency(%)"
    numeric_cols = [
        "Density", "Variability", "Compression_Ratio",
        "CR_File", "Entropy", "P_Score"
    ]

    # Ensure all numeric columns are properly converted to numeric type
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Best grid per domain (assuming pre-identified best grid)
    best_grids = df.loc[df.groupby("Domain")["P_Score"].idxmax()][['Domain', 'Dataset_Type', 'Site_Type', 'Grid_Size'] + numeric_cols + ["Grid_Consistency(%)"]]

    # Make sure that the 'Grid_Size' column exists in best_grids
    if 'Grid_Size' not in best_grids.columns:
        print("'Grid_Size' column is missing in best_grids.")
        return

    # Summary statistics
    print("\n--- Overall Stats (Best Grid Per Domain) ---")
    print(best_grids[numeric_cols + ["Grid_Consistency(%)"]].describe())

    # Correlation matrix (sanity check)
    corr_matrix = best_grids[numeric_cols].corr()
    print("\n--- Correlation Matrix ---")
    print(corr_matrix)

    # Correlation with P_Score
    score_corr = corr_matrix["P_Score"].sort_values(ascending=False)
    print("\n--- Correlation of P_Score with Input Metrics ---")
    print(score_corr)

    # Grouped stats by dataset type and site type - only using numeric columns for aggregation
    best_grids_numeric = best_grids[numeric_cols + ['Dataset_Type', 'Site_Type']]  # Filter out non-numeric columns
    grouped = best_grids_numeric.groupby(["Dataset_Type", "Site_Type"]).agg(['mean', 'std', 'count'])
    grouped.to_csv(os.path.join(UI_DATA_DIR, "final_evaluation_stats.csv"))

    # Hypothesis testing: CR_File ≈ 1 / (Entropy × Density)
    print("\n--- Hypothesis: CR_File ≈ 1 / (Entropy × Density) ---")
    best_grids["Entropy*Density"] = best_grids["Entropy"] * best_grids["Density"]
    best_grids["Expected_CR"] = 1 / best_grids["Entropy*Density"]
    best_grids["CR_Diff"] = best_grids["Expected_CR"] - best_grids["CR_File"]

    # Linear regression
    model = LinearRegression().fit(
        best_grids[["Entropy*Density"]], best_grids["CR_File"]
    )
    r2 = model.score(best_grids[["Entropy*Density"]], best_grids["CR_File"])
    print(f"🔍 R² score: {r2:.4f}")

    best_grids.to_csv(os.path.join(UI_DATA_DIR, "cr_hypothesis_analysis.csv"), index=False)

    # Plot 1: CR_File vs Entropy × Density
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=best_grids, x="Entropy*Density", y="CR_File", hue="Dataset_Type")
    plt.plot(best_grids["Entropy*Density"], model.predict(best_grids[["Entropy*Density"]]),
             color='black', linestyle='--', label="Regression Line")
    plt.title("CR_File vs Entropy × Density")
    plt.xlabel("Entropy × Density")
    plt.ylabel("CR_File")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "scatter_cr_file_vs_entropy_density.png"))

    # Plot 2: Correlation Heatmap (without Grid_Consistency(%) in correlation)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Heatmap of Metrics")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "correlation_heatmap.png"))

    # Plot 3: Grid Consistency by Dataset Type (with corrected hue parameter)
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=best_grids, x="Dataset_Type", y="Grid_Consistency(%)", hue="Dataset_Type", palette="Set2", legend=False)
    plt.title("Grid Consistency (%) by Dataset Type")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "grid_consistency_by_type.png"))

    # Plot 4: P_Score vs Metrics
    plt.figure(figsize=(8, 5))
    score_corr.drop("P_Score").plot(kind='barh', color='teal')
    plt.title("Correlation of P_Score with Metrics")
    plt.xlabel("Pearson Correlation")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "p_score_metric_correlation.png"))

    # --- New Plots: ---
    # Plot 5: Parsing Score across Grid Sizes
    grid_size_comparison = best_grids.groupby("Grid_Size")["P_Score"].mean()
    plt.figure(figsize=(8, 6))
    grid_size_comparison.plot(kind='bar', color='royalblue')
    plt.title("Parsing Score Across Grid Sizes")
    plt.xlabel("Grid Size")
    plt.ylabel("Mean P_Score")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "parsing_score_across_grid_sizes.png"))

    # Plot 6: Best Grid Size per Domain
    best_grid_per_domain = best_grids.groupby("Domain")["Grid_Size"].agg(lambda x: x.mode()[0])  # most frequent grid size
    plt.figure(figsize=(8, 6))
    best_grid_per_domain.value_counts().plot(kind='bar', color='forestgreen')
    plt.title("Best Grid Size per Domain")
    plt.xlabel("Grid Size")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "best_grid_size_per_domain.png"))

    # Plot 7: Train (E-Commerce) vs Test (Media) Comparison for P_Score and Density
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Dataset_Type", y="P_Score", data=best_grids, hue="Dataset_Type", palette="Set2", legend=False)
    plt.title("Train vs Test: P_Score Comparison")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "train_vs_test_p_score_comparison.png"))

    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Dataset_Type", y="Density", data=best_grids, hue="Dataset_Type", palette="Set2", legend=False)
    plt.title("Train vs Test: Density Comparison")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "train_vs_test_density_comparison.png"))

    print("\nStep 8 completed. All results exported.")

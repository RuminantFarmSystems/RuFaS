import pandas as pd


def raw_compare_csvs(file_a, file_b):
    df_a = pd.read_csv(file_a)
    df_b = pd.read_csv(file_b)

    # Identify row identifier (leftmost column)
    idx_col = df_a.columns[0]

    # Set index
    df_a = df_a.set_index(idx_col)
    df_b = df_b.set_index(idx_col)

    # Restrict to matching rows
    common_rows = df_a.index.intersection(df_b.index)
    df_a = df_a.loc[common_rows].sort_index()
    df_b = df_b.loc[common_rows].sort_index()

    # Restrict to matching columns
    common_cols = df_a.columns.intersection(df_b.columns)
    df_a = df_a[common_cols]
    df_b = df_b[common_cols]

    # Force numeric values
    df_a = df_a.apply(pd.to_numeric, errors="coerce")
    df_b = df_b.apply(pd.to_numeric, errors="coerce")

    # Drop columns entirely NaN in BOTH files
    non_empty_cols = [col for col in common_cols if not (df_a[col].isna().all() and df_b[col].isna().all())]
    df_a = df_a[non_empty_cols]
    df_b = df_b[non_empty_cols]

    return df_a, df_b


def percent_compare_csvs(df_a, df_b):
    # Compute percentage safely (B as % of A)
    percent_df = (df_b - df_a) / df_a * 100

    # Avoid divide‑by‑zero artifacts
    percent_df[df_a == 0] = pd.NA

    return percent_df


def diff_compare_csvs(df_a, df_b):
    # Compute percentage safely (B as % of A)
    diff_df = df_b - df_a

    # Avoid divide‑by‑zero artifacts
    diff_df[df_a == 0] = pd.NA

    return diff_df


newfilename = "20260512"

# File A (reference)
FILE_A = r"input\data\EEE\full_feeds_land_use_change_emissions_July2024_interpolated_regional_average.csv"
# File B (new being compared)
FILE_B = rf"input\data\EEE\feed_emissions_luc_{newfilename}_interpolated_regional_average.csv"

dfa, dfb = raw_compare_csvs(FILE_A, FILE_B)
percent_diff = percent_compare_csvs(dfa, dfb)
print(percent_diff)
percent_diff.to_csv(rf"helpful_scripts\emissions_interpolation\feed_emissions_luc_{newfilename}_percent_comparison.csv")


dfa, dfb = raw_compare_csvs(FILE_A, FILE_B)
percent_diff = diff_compare_csvs(dfa, dfb)
print(diff_diff)
diff_diff.to_csv(rf"helpful_scripts\emissions_interpolation\feed_emissions_luc_{newfilename}_comparison.csv")


# File A (original)
FILE_A = r"input\data\EEE\full_feeds_emissions_July2024_interpolated_regional_average.csv"
# File B (new being compared)
FILE_B = rf"input\data\EEE\feed_emissions_total_{newfilename}_interpolated_regional_average.csv"

dfa, dfb = raw_compare_csvs(FILE_A, FILE_B)
percent_diff = percent_compare_csvs(dfa, dfb)
print(percent_diff)
percent_diff.to_csv(
    rf"helpful_scripts\emissions_interpolation\feed_emissions_total_{newfilename}_percent_comparison.csv"
)

diff_diff = diff_compare_csvs(dfa, dfb)
print(diff_diff)
diff_diff.to_csv(rf"helpful_scripts\emissions_interpolation\feed_emissions_total_{filename}_comparison.csv")

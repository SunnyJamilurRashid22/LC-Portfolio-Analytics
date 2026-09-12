import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parents[1] / "data" / "Export_Bill_Portfolio_Anonymized.xlsx"

df = pd.read_excel(file_path, skiprows=4)

df.columns = df.columns.str.strip().str.strip('"')

print("Dataset loaded successfully!")
print("Rows and columns:", df.shape)

print("\nFC Purchase availability:")
print(df["FC Purchase"].notna().value_counts())

print("\nPurchase field availability:")
print(
    pd.crosstab(
        df["FC Purchase"].notna(),
        df["BDT Purchase"].notna()
    )
)

print("\nTotal Purchase Amount:")
print(df["Total Purchase amount"].describe())

print("\nTotal Purchase Amount = 0:")
print((df["Total Purchase amount"] == 0).value_counts())

df["Purchase Status"] = df["Total Purchase amount"].apply(
    lambda x: "Purchased" if x > 0 else "Not Purchased"
)

print("\nPurchase Status:")
print(df["Purchase Status"].value_counts())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nDuplicate Bill Numbers:")
print(df["Bill No."].duplicated().sum())

print("\nLC/Contract Number Analysis:")
print("Total records:", len(df))
print("Unique LC/Contract Numbers:", df["LC/Contract No."].nunique())

lc_bill_count = df.groupby("LC/Contract No.").size()

print("\nBills per LC/Contract:")
print(lc_bill_count.describe())

multiple_bill_lcs = lc_bill_count[lc_bill_count > 1]

print("\nNumber of LC/Contracts with multiple bills:")
print(len(multiple_bill_lcs))

print("\nTop 10 LC/Contracts by number of bills:")
print(
    multiple_bill_lcs
    .sort_values(ascending=False)
    .head(10)
)

print("\n71VK2500000647 Summary:")

lc_71vk = df[
    df["LC/Contract No."] == "71VK2500000647"
]

print("Number of bills:", len(lc_71vk))
print("Total Bill Value:", lc_71vk["Bill Value"].sum())
print("Total Outstanding:", lc_71vk["Bill Outstanding in FC"].sum())
print("Total Purchase:", lc_71vk["Total Purchase amount"].sum())
print("Total Un-purchased:", lc_71vk["Un-purchased amount in FC"].sum())

print("\nPortfolio Reconciliation:")

df["Purchase + Unpurchased"] = (
    df["Total Purchase amount"]
    + df["Un-purchased amount in FC"]
)

df["Reconciliation Difference"] = (
    df["Bill Outstanding in FC"]
    - df["Purchase + Unpurchased"]
)

print(df["Reconciliation Difference"].describe())

df["Reconciliation Status"] = df[
    "Reconciliation Difference"
].abs().apply(
    lambda x: "OK" if x < 0.01 else "Check"
)

print("\nReconciliation Status:")
print(df["Reconciliation Status"].value_counts())

reconciliation_issues = df[
    df["Reconciliation Status"] == "Check"
]

print("\nGenuine Reconciliation Issues:")
print("Number of records:", len(reconciliation_issues))

print(
    reconciliation_issues[
        [
            "Bill No.",
            "LC/Contract No.",
            "Currency",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Reconciliation Difference"
        ]
    ]
    .sort_values("Reconciliation Difference")
    .head(20)
)
issues = df[
    df["Reconciliation Status"] == "Check"
].copy()

columns_to_check = [
    "Bill No.",
    "Bill Date",
    "Bill Type",
    "Currency",
    "Bill Value",
    "Bill Outstanding in FC",
    "Total Purchase amount",
    "FC Purchase",
    "BDT Purchase",
    "Un-purchased amount in FC",
    "Purchase Status",
    "LC/Contract No.",
    "Group ID",
    "Applicant/Buyer Name",
    "Beneficiary/Seller",
    "Tenor Days",
    "Acceptance(Y/N)",
    "Maturity Date",
    "Reconciliation Difference"
]

print(
    issues[
        columns_to_check
    ].sort_values(
        "Reconciliation Difference"
    ).head(10).to_string(index=False)
)

print("\nPortfolio Exposure:")

print(
    "Total Bill Value:",
    df["Bill Value"].sum()
)

print(
    "Total Outstanding:",
    df["Bill Outstanding in FC"].sum()
)

print(
    "Total Purchase:",
    df["Total Purchase amount"].sum()
)

print(
    "Total Un-purchased:",
    df["Un-purchased amount in FC"].sum()
)
print("\nCurrency Exposure:")

currency_exposure = (
    df.groupby("Currency")
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchase=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

print(currency_exposure)

print("\nPurchase Status by Currency:")

purchase_by_currency = (
    df.groupby(["Currency", "Purchase Status"])
      .agg(
          Bills=("Bill No.", "count"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchase=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
)

print(purchase_by_currency)

print("\nTop Customers by Outstanding Exposure:")

customer_exposure = (
    df.groupby("Beneficiary/Seller")
      .agg(
          Bills=("Bill No.", "count"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchase=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

print(customer_exposure.head(20))

print("\nCustomer Exposure by Currency:")

customer_currency = (
    df.groupby(
        ["Currency", "Beneficiary/Seller"]
    )
    .agg(
        Bills=("Bill No.", "count"),
        Outstanding=("Bill Outstanding in FC", "sum"),
        Purchase=("Total Purchase amount", "sum"),
        Unpurchased=("Un-purchased amount in FC", "sum")
    )
    .sort_values(
        ["Currency", "Outstanding"],
        ascending=[True, False]
    )
)

print(customer_currency.head(30))

print("\nCurrency Concentration Analysis:")

currency_analysis = (
    df.groupby("Currency")
    .agg(
        Bills=("Bill No.", "count"),
        Bill_Value=("Bill Value", "sum"),
        Outstanding=("Bill Outstanding in FC", "sum"),
        Purchase=("Total Purchase amount", "sum"),
        Unpurchased=("Un-purchased amount in FC", "sum")
    )
)

currency_analysis["Outstanding_%"] = (
    currency_analysis["Outstanding"]
    / currency_analysis["Outstanding"].sum()
    * 100
)

currency_analysis["Purchase_%"] = (
    currency_analysis["Purchase"]
    / currency_analysis["Purchase"].sum()
    * 100
)

currency_analysis["Unpurchased_%"] = (
    currency_analysis["Unpurchased"]
    / currency_analysis["Unpurchased"].sum()
    * 100
)

print(currency_analysis.sort_values(
    "Outstanding",
    ascending=False
))

print("\nCustomer Concentration by Currency:")

customer_currency = (
    df.groupby(
        ["Currency", "Beneficiary/Seller"]
    )
    .agg(
        Bills=("Bill No.", "count"),
        Outstanding=("Bill Outstanding in FC", "sum"),
        Purchase=("Total Purchase amount", "sum"),
        Unpurchased=("Un-purchased amount in FC", "sum")
    )
)
currency_totals = (
    customer_currency
    .groupby(level="Currency")["Outstanding"]
    .transform("sum")
)
customer_currency["Outstanding_%"] = (
    customer_currency["Outstanding"]
    / currency_totals
    * 100
)

customer_currency = customer_currency.sort_values(
    ["Currency", "Outstanding"],
    ascending=[True, False]
)

print(customer_currency)
print("\nTop 5 Customer Concentration by Currency:")

top5_concentration = (
    customer_currency
    .groupby(level="Currency")["Outstanding_%"]
    .head(5)
    .groupby(level="Currency")
    .sum()
    .sort_values(ascending=False)
)

print(top5_concentration)
print("\nCustomer Purchase Utilization by Currency:")

customer_utilization = (
    df.groupby(
        ["Currency", "Beneficiary/Seller"]
    )
    .agg(
        Bills=("Bill No.", "count"),
        Outstanding=("Bill Outstanding in FC", "sum"),
        Purchase=("Total Purchase amount", "sum"),
        Unpurchased=("Un-purchased amount in FC", "sum")
    )
)

customer_utilization["Purchase_Utilization_%"] = (
    customer_utilization["Purchase"]
    / customer_utilization["Outstanding"]
    * 100
)

customer_utilization = (
    customer_utilization
    .replace([float("inf"), -float("inf")], 0)
    .fillna(0)
    .sort_values(
        ["Currency", "Purchase_Utilization_%"],
        ascending=[True, False]
    )
)

print(customer_utilization.head(30))

print("\nPurchase Field Relationship Check:")

df["Purchase_plus_Unpurchased"] = (
    df["Total Purchase amount"]
    + df["Un-purchased amount in FC"]
)

df["Difference"] = (
    df["Bill Outstanding in FC"]
    - df["Purchase_plus_Unpurchased"]
)

print(
    df[
        [
            "Currency",
            "Bill No.",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Difference"
        ]
    ].head(20)
)

print("\nDifference Statistics:")

print(
    df["Difference"].describe()
)
print("\nPurchase Relationship Exceptions:")

exceptions = df[df["Difference"] < -0.01]

print("Number of exceptions:", len(exceptions))

print(
    "Percentage of records:",
    round(len(exceptions) / len(df) * 100, 2),
    "%"
)

print("\nExceptions by Currency:")

print(
    exceptions.groupby("Currency")
    .size()
    .sort_values(ascending=False)
)

print("\nLargest Exceptions:")

print(
    exceptions[
        [
            "Currency",
            "Bill No.",
            "Beneficiary/Seller",
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Difference"
        ]
    ]
    .sort_values("Difference")
    .head(20)
)
print(
    exceptions[
        [
            "Currency",
            "Bill No.",
            "Beneficiary/Seller",
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Difference"
        ]
    ]
    .sort_values("Difference")
    .head(20)
)
print("\nExceptions by Bill Type:")

print(
    exceptions.groupby("Bill Type")
    .size()
    .sort_values(ascending=False)
)
print("\nExceptions by Currency and Bill Type:")

print(
    exceptions.groupby(
        ["Currency", "Bill Type"]
    )
    .size()
    .sort_values(ascending=False)
)
print("\nException Impact by Currency and Bill Type:")

exception_impact = (
    exceptions
    .groupby(["Currency", "Bill Type"])
    .agg(
        Exception_Count=("Difference", "count"),
        Total_Exception_Amount=("Difference", lambda x: x.abs().sum()),
        Largest_Exception=("Difference", lambda x: x.abs().max())
    )
    .sort_values(
        "Total_Exception_Amount",
        ascending=False
    )
)

print(exception_impact)
print("\n" + "=" * 70)
print("EXCEPTION DIAGNOSTIC ANALYSIS")
print("=" * 70)

print("\nException Records by Bill Type:")
print(
    exceptions["Bill Type"]
    .value_counts()
)

print("\nException Records by Currency:")
print(
    exceptions["Currency"]
    .value_counts()
)

print("\nException Records by Applicant/Buyer:")
print(
    exceptions["Applicant/Buyer Name"]
    .value_counts()
)

print("\nException Records by Beneficiary/Seller:")
print(
    exceptions["Beneficiary/Seller"]
    .value_counts()
)
print("\n" + "=" * 70)
print("EXCEPTION RELATIONSHIP ANALYSIS")
print("=" * 70)

print("\nTop Applicants with Exceptions:")

print(
    exceptions["Applicant/Buyer Name"]
    .value_counts()
    .head(10)
)

print("\nTop Beneficiaries with Exceptions:")

print(
    exceptions["Beneficiary/Seller"]
    .value_counts()
    .head(10)
)

print("\nTop LC/Contracts with Exceptions:")

exception_lc_count = (
    exceptions["LC/Contract No."]
    .value_counts()
)

print(exception_lc_count.head(20))
print("\n" + "=" * 70)
print("DETAILED LC/CONTRACT EXCEPTION ANALYSIS")
print("=" * 70)

top_exception_lcs = (
    exceptions["LC/Contract No."]
    .value_counts()
    .head(4)
    .index
)

for lc in top_exception_lcs:

    print("\n" + "-" * 70)
    print("LC/Contract:", lc)

    lc_data = df[df["LC/Contract No."] == lc]

    print("\nNumber of bills:", len(lc_data))

print("\n" + "=" * 70)
print("DETAILED LC/CONTRACT EXCEPTION ANALYSIS")
print("=" * 70)

top_exception_lcs = (
    exceptions["LC/Contract No."]
    .value_counts()
    .head(4)
    .index
)

for lc in top_exception_lcs:

    print("\n" + "-" * 70)
    print("LC/Contract:", lc)

    lc_data = df[df["LC/Contract No."] == lc]

    print("\nNumber of bills:", len(lc_data))

    print(
        lc_data[
            [
                "Bill No.",
                "Bill Date",
                "Bill Type",
                "Currency",
                "Applicant/Buyer Name",
                "Beneficiary/Seller",
                "Bill Value",
                "Bill Outstanding in FC",
                "Total Purchase amount",
                "Un-purchased amount in FC",
                "Difference"
            ]
        ].to_string(index=False)
    )
print("\n" + "=" * 70)
print("STAGE 9.1 — CUSTOMER PORTFOLIO OVERVIEW")
print("=" * 70)

customer_summary = (
    df.groupby("Applicant/Buyer Name")
    .agg(
        Bills=("Bill No.", "count"),
        Bill_Value=("Bill Value", "sum"),
        Outstanding=("Bill Outstanding in FC", "sum"),
        Purchase=("Total Purchase amount", "sum"),
        Unpurchased=("Un-purchased amount in FC", "sum")
    )
    .sort_values("Outstanding", ascending=False)
)

print(customer_summary.head(20))
print("\n" + "=" * 70)
print("STAGE 9.2 — CUSTOMER NAME QUALITY CHECK")
print("=" * 70)

print(
    "Total unique Applicant/Buyer names:",
    df["Applicant/Buyer Name"].nunique()
)

print(
    "\nMissing Applicant/Buyer names:",
    df["Applicant/Buyer Name"].isna().sum()
)

print("\nNames containing MAX:")
print(
    df[
        df["Applicant/Buyer Name"]
        .astype(str)
        .str.contains("MAX", case=False, na=False)
    ]["Applicant/Buyer Name"]
    .value_counts()
)
print("\n" + "=" * 70)
print("TOP 30 APPLICANT/BUYER CUSTOMERS")
print("=" * 70)

print(
    customer_summary[
        [
            "Bills",
            "Bill_Value",
            "Outstanding",
            "Purchase",
            "Unpurchased"
        ]
    ]
    .head(30)
    .to_string()
)
customer_summary["Bill_Value_%"] = (
    customer_summary["Bill_Value"]
    / customer_summary["Bill_Value"].sum()
    * 100
)

print("\nTop 10 Customers by Bill Value:")

print(
    customer_summary[
        [
            "Bills",
            "Bill_Value",
            "Bill_Value_%"
        ]
    ]
    .sort_values("Bill_Value", ascending=False)
    .head(10)
    .to_string()
)
print("\n" + "=" * 70)
print("STAGE 9.3 — CUSTOMER CONCENTRATION")
print("=" * 70)

customer_summary["Outstanding_%"] = (
    customer_summary["Outstanding"]
    / customer_summary["Outstanding"].sum()
    * 100
)

top_5_concentration = (
    customer_summary.head(5)["Outstanding_%"].sum()
)

top_10_concentration = (
    customer_summary.head(10)["Outstanding_%"].sum()
)

print("\nTop 10 Customers by Outstanding:")

print(
    customer_summary[
        [
            "Bills",
            "Outstanding",
            "Outstanding_%"
        ]
    ]
    .head(10)
    .to_string()
)

print(
    "\nTop 5 Customer Concentration:",
    round(top_5_concentration, 2),
    "%"
)

print(
    "Top 10 Customer Concentration:",
    round(top_10_concentration, 2),
    "%"
)
print("\n" + "=" * 70)
print("STAGE 9.4 — CUSTOMER PURCHASE BEHAVIOUR")
print("=" * 70)

customer_summary["Purchase_%"] = (
    customer_summary["Purchase"]
    / customer_summary["Bill_Value"]
    * 100
)

print("\nTop 15 Customers by Purchase Amount:")

print(
    customer_summary[
        [
            "Bills",
            "Bill_Value",
            "Purchase",
            "Unpurchased",
            "Purchase_%"
        ]
    ]
    .sort_values("Purchase", ascending=False)
    .head(15)
    .to_string()
)
print("\n" + "=" * 70)
print("STAGE 9.5 — CUSTOMER UTILIZATION ANALYSIS")
print("=" * 70)

print("\nHighest Purchase Utilization — minimum 5 bills:")

high_utilization = (
    customer_summary[
        customer_summary["Bills"] >= 5
    ]
    .sort_values("Purchase_%", ascending=False)
)

print(
    high_utilization[
        [
            "Bills",
            "Bill_Value",
            "Purchase",
            "Unpurchased",
            "Purchase_%"
        ]
    ]
    .head(15)
    .to_string()
)

print("\nLowest Purchase Utilization — minimum 5 bills:")

low_utilization = (
    customer_summary[
        customer_summary["Bills"] >= 5
    ]
    .sort_values("Purchase_%", ascending=True)
)

print(
    low_utilization[
        [
            "Bills",
            "Bill_Value",
            "Purchase",
            "Unpurchased",
            "Purchase_%"
        ]
    ]
    .head(15)
    .to_string()
)
print("\n" + "=" * 70)
print("STAGE 9.6 — CUSTOMER SIZE VS UTILIZATION")
print("=" * 70)

customer_analysis = customer_summary.copy()

# Exclude customers with no meaningful bill value
customer_analysis = customer_analysis[
    customer_analysis["Bill_Value"] > 0
]

# Median customer bill value
median_bill_value = customer_analysis["Bill_Value"].median()

print(
    "\nMedian customer Bill Value:",
    round(median_bill_value, 2)
)

# Customer segments
customer_analysis["Size_Segment"] = customer_analysis[
    "Bill_Value"
].apply(
    lambda x: "High Value" if x >= median_bill_value else "Low Value"
)

customer_analysis["Utilization_Segment"] = customer_analysis[
    "Purchase_%"
].apply(
    lambda x: "High Utilization" if x >= 50 else "Low Utilization"
)

print("\nCustomer Segment Distribution:")

print(
    customer_analysis[
        ["Size_Segment", "Utilization_Segment"]
    ]
    .value_counts()
)

print("\nHigh Value + High Utilization:")

print(
    customer_analysis[
        (customer_analysis["Size_Segment"] == "High Value") &
        (customer_analysis["Utilization_Segment"] == "High Utilization")
    ][
        [
            "Bills",
            "Bill_Value",
            "Purchase",
            "Unpurchased",
            "Purchase_%"
        ]
    ]
    .sort_values("Bill_Value", ascending=False)
    .head(15)
    .to_string()
)

print("\nHigh Value + Low Utilization:")

print(
    customer_analysis[
        (customer_analysis["Size_Segment"] == "High Value") &
        (customer_analysis["Utilization_Segment"] == "Low Utilization")
    ][
        [
            "Bills",
            "Bill_Value",
            "Purchase",
            "Unpurchased",
            "Purchase_%"
        ]
    ]
    .sort_values("Bill_Value", ascending=False)
    .head(15)
    .to_string()
)
print("\n" + "=" * 70)
print("STAGE 9.6 — CUSTOMER SIZE VS UTILIZATION")
print("=" * 70)

customer_analysis = customer_summary.copy()

customer_analysis = customer_analysis[
    customer_analysis["Bill_Value"] > 0
]

median_bill_value = customer_analysis["Bill_Value"].median()

print(
    "\nMedian customer Bill Value:",
    round(median_bill_value, 2)
)

customer_analysis["Size_Segment"] = customer_analysis[
    "Bill_Value"
].apply(
    lambda x: "High Value" if x >= median_bill_value else "Low Value"
)

customer_analysis["Utilization_Segment"] = customer_analysis[
    "Purchase_%"
].apply(
    lambda x: "High Utilization" if x >= 50 else "Low Utilization"
)

print("\nCustomer Segment Distribution:")

print(
    customer_analysis[
        ["Size_Segment", "Utilization_Segment"]
    ]
    .value_counts()
)

print("\nHigh Value + High Utilization:")

print(
    customer_analysis[
        (customer_analysis["Size_Segment"] == "High Value") &
        (customer_analysis["Utilization_Segment"] == "High Utilization")
    ][
        [
            "Bills",
            "Bill_Value",
            "Purchase",
            "Unpurchased",
            "Purchase_%"
        ]
    ]
    .sort_values("Bill_Value", ascending=False)
    .head(15)
    .to_string()
)

print("\nHigh Value + Low Utilization:")

print(
    customer_analysis[
        (customer_analysis["Size_Segment"] == "High Value") &
        (customer_analysis["Utilization_Segment"] == "Low Utilization")
    ][
        [
            "Bills",
            "Bill_Value",
            "Purchase",
            "Unpurchased",
            "Purchase_%"
        ]
    ]
    .sort_values("Bill_Value", ascending=False)
    .head(15)
    .to_string()
)
print("\n" + "=" * 70)
print("STAGE 10.1 — TENOR ANALYSIS")
print("=" * 70)

print("\nTenor Days — Summary Statistics:")

print(
    df["Tenor Days"].describe()
)

print("\nTenor Description Distribution:")

print(
    df["Tenor Description"]
    .value_counts(dropna=False)
)

print("\nTop 15 Tenor Days:")

print(
    df["Tenor Days"]
    .value_counts()
    .sort_index()
    .head(15)
)
print("\n" + "=" * 70)
print("STAGE 10.2 — ACCEPTANCE ANALYSIS")
print("=" * 70)

print("\nAcceptance Distribution:")

print(
    df["Acceptance(Y/N)"]
    .value_counts(dropna=False)
)

print("\nAcceptance Percentage:")

print(
    df["Acceptance(Y/N)"]
    .value_counts(normalize=True, dropna=False) * 100
)
print("\n" + "=" * 70)
print("STAGE 10.2A — ACCEPTANCE VS TENOR")
print("=" * 70)

print("\nAverage Tenor by Acceptance Status:")

print(
    df.groupby("Acceptance(Y/N)")["Tenor Days"]
      .agg(["count", "mean", "median", "min", "max"])
)

print("\nTenor Description by Acceptance Status:")

print(
    pd.crosstab(
        df["Acceptance(Y/N)"],
        df["Tenor Description"],
        margins=True
    )
)
print("\n" + "=" * 70)
print("STAGE 10.2B — ACCEPTANCE VS FINANCIAL EXPOSURE")
print("=" * 70)

acceptance_exposure = (
    df.groupby("Acceptance(Y/N)", dropna=False)
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchase=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum"),
          Avg_Bill_Value=("Bill Value", "mean"),
          Avg_Outstanding=("Bill Outstanding in FC", "mean")
    )
)

print("\nAcceptance Exposure Summary:")
print(acceptance_exposure)
print("\n" + "=" * 70)
print("STAGE 10.3 — OUTSTANDING VS UNPURCHASED EXPOSURE")
print("=" * 70)

print("\nPortfolio Exposure Summary:")

print(
    df[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ].sum()
)

print("\nAverage Exposure per Bill:")

print(
    df[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ].mean()
)
print("\n" + "=" * 70)
print("STAGE 10.4 — OUTSTANDING EXPOSURE BY TRANSACTION TYPE")
print("=" * 70)

print("\nExposure by Bill Type:")

exposure_by_type = (
    df.groupby("Bill Type")[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ]
    .sum()
    .sort_values("Bill Outstanding in FC", ascending=False)
)

print(exposure_by_type)
print("\nOutstanding Exposure Share (%):")

print(
    (
        exposure_by_type["Bill Outstanding in FC"]
        / exposure_by_type["Bill Outstanding in FC"].sum()
        * 100
    ).round(2)
)
print("\n" + "=" * 70)
print("STAGE 10.5 — PURCHASED VS UN-PURCHASED BY BILL TYPE")
print("=" * 70)

print("\nPurchase Status by Bill Type:")

print(
    df.groupby(["Bill Type", "Purchase Status"])[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ]
    .sum()
)
print("\nRecord Count by Bill Type and Purchase Status:")

print(
    df.groupby(["Bill Type", "Purchase Status"])
      .size()
)
print("\n" + "=" * 70)
print("STAGE 10.6 — PARTIALLY PURCHASED BILLS")
print("=" * 70)

partial_purchase = df[
    (df["Purchase Status"] == "Purchased") &
    (df["Un-purchased amount in FC"] > 0)
]

print("\nPartially Purchased Bill Count:")
print(len(partial_purchase))

print("\nPartially Purchased Exposure:")

print(
    partial_purchase[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ].sum()
)

print("\nPartially Purchased Bills by Bill Type:")

print(
    partial_purchase.groupby("Bill Type")[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ].sum()
)
print("\n" + "=" * 70)
print("STAGE 10.7 — FULL VS PARTIAL UN-PURCHASED EXPOSURE")
print("=" * 70)

df["Purchase Category"] = "Fully Unpurchased"

df.loc[
    (df["Purchase Status"] == "Purchased") &
    (df["Un-purchased amount in FC"] > 0),
    "Purchase Category"
] = "Partially Purchased"

print("\nPurchase Category Summary:")

print(
    df.groupby("Purchase Category")[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ].sum()
)

print("\nRecord Count:")

print(
    df["Purchase Category"].value_counts()
)
print("\n" + "=" * 70)
print("STAGE 10.8 — FINAL PURCHASE STATE RECONCILIATION")
print("=" * 70)

df["Purchase State"] = "Not Purchased"

df.loc[
    (df["Purchase Status"] == "Purchased") &
    (df["Un-purchased amount in FC"] > 0),
    "Purchase State"
] = "Partially Purchased"

df.loc[
    (df["Purchase Status"] == "Purchased") &
    (df["Un-purchased amount in FC"] == 0),
    "Purchase State"
] = "Fully Purchased"

print("\nPurchase State Record Count:")
print(df["Purchase State"].value_counts())

print("\nPurchase State Exposure:")
print(
    df.groupby("Purchase State")[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ].sum()
)
print("\n" + "=" * 70)
print("STAGE 10.9 — PURCHASE STATUS ANOMALY")
print("=" * 70)

anomaly = df[
    (df["Purchase Status"] == "Purchased") &
    ~(df["Un-purchased amount in FC"] > 0)
]

print("\nAnomalous Purchased Record Count:")
print(len(anomaly))

print("\nAnomalous Record:")

print(
    anomaly[
        [
            "Bill No.",
            "Bill Type",
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Purchase Status"
        ]
    ].to_string(index=False)
)
print("\n" + "=" * 70)
print("ANOMALOUS PURCHASE — CLIENT DETAILS")
print("=" * 70)

anomaly = df[
    (df["Purchase Status"] == "Purchased") &
    ~(df["Un-purchased amount in FC"] > 0)
]

print(
    anomaly[
        [
            "Bill No.",
            "Customer ID",
            "Applicant/Buyer Name",
            "Beneficiary/Seller",
            "Branch Name",
            "Business Segment",
            "Line of Business",
            "Bill Type",
            "Currency",
            "Bill Value",
            "Bill Outstanding in FC",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "LC/Contract No."
        ]
    ].to_string(index=False)
)
print("\n" + "=" * 70)
print("STAGE 10.10 — BILL VALUE VS OUTSTANDING GAP")
print("=" * 70)

df["Outstanding Gap"] = (
    df["Bill Value"] - df["Bill Outstanding in FC"]
)

print("\nPortfolio Outstanding Gap:")
print(df["Outstanding Gap"].sum())

print("\nOutstanding Gap by Bill Type:")

print(
    df.groupby("Bill Type")[
        ["Bill Value", "Bill Outstanding in FC", "Outstanding Gap"]
    ].sum()
)

print("\nOutstanding Gap by Purchase Status:")

print(
    df.groupby("Purchase Status")[
        ["Bill Value", "Bill Outstanding in FC", "Outstanding Gap"]
    ].sum()
)
print("\n" + "=" * 70)
print("STAGE 10.11 — COLLECTION-UNDER-LC OUTSTANDING GAP")
print("=" * 70)

lc_gap = df[
    (df["Bill Type"] == "Collection-Under LC") &
    (df["Outstanding Gap"] != 0)
].copy()

print("\nRecords with Bill Value ≠ Outstanding:")
print(len(lc_gap))

print("\nGap Summary:")
print(
    lc_gap[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Outstanding Gap"
        ]
    ].sum()
)

print("\nGap Statistics:")
print(
    lc_gap["Outstanding Gap"].describe()
)
print("\nTop 20 Collection-Under-LC Records by Outstanding Gap:")

print(
    lc_gap[
        [
            "Bill No.",
            "Customer ID",
            "Applicant/Buyer Name",
            "Bill Value",
            "Bill Outstanding in FC",
            "Outstanding Gap",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Purchase Status",
            "LC/Contract No."
        ]
    ]
    .sort_values("Outstanding Gap", ascending=False)
    .head(20)
    .to_string(index=False)
)
print("\n" + "=" * 70)
print("STAGE 10.12 — OUTSTANDING GAP CONCENTRATION BY CUSTOMER")
print("=" * 70)

customer_gap = (
    lc_gap
    .groupby(["Customer ID", "Applicant/Buyer Name"], dropna=False)
    .agg(
        Records=("Bill No.", "count"),
        Bill_Value=("Bill Value", "sum"),
        Outstanding=("Bill Outstanding in FC", "sum"),
        Outstanding_Gap=("Outstanding Gap", "sum")
    )
    .sort_values("Outstanding_Gap", ascending=False)
)

print("\nOutstanding Gap by Customer:")

print(
    customer_gap
    .head(20)
    .to_string()
)

print("\nTotal Gap:", lc_gap["Outstanding Gap"].sum())

print("\nTop 5 Customer Gap:")
print(customer_gap.head(5)["Outstanding_Gap"].sum())

print(
    "\nTop 5 Customer Gap Share:",
    round(
        customer_gap.head(5)["Outstanding_Gap"].sum()
        / lc_gap["Outstanding Gap"].sum() * 100,
        2
    ),
    "%"
)
print("\n" + "=" * 70)
print("STAGE 10.13 — OUTSTANDING GAP CONCENTRATION BY LC/CONTRACT")
print("=" * 70)

lc_contract_gap = (
    lc_gap
    .groupby(
        ["LC/Contract No.", "Customer ID", "Applicant/Buyer Name"],
        dropna=False
    )
    .agg(
        Records=("Bill No.", "count"),
        Bill_Value=("Bill Value", "sum"),
        Outstanding=("Bill Outstanding in FC", "sum"),
        Outstanding_Gap=("Outstanding Gap", "sum")
    )
    .sort_values("Outstanding_Gap", ascending=False)
)

print("\nOutstanding Gap by LC/Contract:")

print(
    lc_contract_gap
    .head(20)
    .to_string()
)

print("\nTotal Gap:", lc_gap["Outstanding Gap"].sum())

print("\nTop 5 LC/Contract Gap:")

top5_lc_gap = lc_contract_gap.head(5)["Outstanding_Gap"].sum()

print(top5_lc_gap)

print(
    "\nTop 5 LC/Contract Gap Share:",
    round(
        top5_lc_gap
        / lc_gap["Outstanding Gap"].sum() * 100,
        2
    ),
    "%"
)
print("\n" + "=" * 70)
print("STAGE 10.14 — TOP LC/CONTRACT GAP DEEP DIVE")
print("=" * 70)

top_lc_contracts = (
    lc_contract_gap
    .head(5)
    .reset_index()["LC/Contract No."]
    .tolist()
)

top_lc_details = df[
    (df["Bill Type"] == "Collection-Under LC") &
    (df["LC/Contract No."].isin(top_lc_contracts))
].copy()

print("\nTop LC/Contract Transaction Details:")

print(
    top_lc_details[
        [
            "LC/Contract No.",
            "Bill No.",
            "Customer ID",
            "Applicant/Buyer Name",
            "Bill Date",
            "Currency",
            "Bill Value",
            "Bill Outstanding in FC",
            "Outstanding Gap",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Purchase Status"
        ]
    ]
    .sort_values(
        ["LC/Contract No.", "Outstanding Gap"],
        ascending=[True, False]
    )
    .to_string(index=False)
)
print("\n" + "=" * 70)
print("STAGE 10.15 — OUTSTANDING GAP VS PURCHASE RECONCILIATION")
print("=" * 70)

gap_purchase = lc_gap[
    [
        "Bill No.",
        "Bill Value",
        "Bill Outstanding in FC",
        "Outstanding Gap",
        "Total Purchase amount",
        "Un-purchased amount in FC",
        "Purchase Status"
    ]
].copy()

gap_purchase["Gap / Bill Value %"] = (
    gap_purchase["Outstanding Gap"]
    / gap_purchase["Bill Value"]
    * 100
)

gap_purchase["Purchase / Gap %"] = (
    gap_purchase["Total Purchase amount"]
    / gap_purchase["Outstanding Gap"]
    * 100
).replace([float("inf"), -float("inf")], None)

print("\nGap vs Purchase:")

print(
    gap_purchase
    .sort_values("Outstanding Gap", ascending=False)
    .to_string(index=False)
)

print("\nPortfolio totals:")

print(
    gap_purchase[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Outstanding Gap",
            "Total Purchase amount",
            "Un-purchased amount in FC"
        ]
    ].sum()
)

print("\nNumber of gap records with purchase > 0:")
print(
    (gap_purchase["Total Purchase amount"] > 0).sum()
)

print("\nNumber of gap records with purchase = 0:")
print(
    (gap_purchase["Total Purchase amount"] == 0).sum()
)
print("\n" + "=" * 70)
print("STAGE 10.16 — PURCHASE VS NON-PURCHASE GAP CONTRIBUTION")
print("=" * 70)

gap_purchase = lc_gap.copy()

gap_purchase["Purchase Group"] = gap_purchase[
    "Total Purchase amount"
].apply(
    lambda v: "Purchase > 0" if v > 0 else "Purchase = 0"
)

gap_purchase_summary = (
    gap_purchase
    .groupby("Purchase Group")
    .agg({
        "Bill No.": "count",
        "Bill Value": "sum",
        "Bill Outstanding in FC": "sum",
        "Outstanding Gap": "sum",
        "Total Purchase amount": "sum",
        "Un-purchased amount in FC": "sum"
    })
    .rename(columns={
        "Bill No.": "Records",
        "Bill Value": "Bill_Value",
        "Bill Outstanding in FC": "Outstanding",
        "Outstanding Gap": "Outstanding_Gap",
        "Total Purchase amount": "Purchase",
        "Un-purchased amount in FC": "Unpurchased"
    })
    .sort_values("Outstanding_Gap", ascending=False)
)

total_gap = lc_gap["Outstanding Gap"].sum()

gap_purchase_summary["Gap Share %"] = (
    gap_purchase_summary["Outstanding_Gap"]
    / total_gap
    * 100
)

print("\nGap Contribution by Purchase Group:")

print(
    gap_purchase_summary.to_string()
)

print("\nGap Share:")

print(
    gap_purchase_summary[
        [
            "Records",
            "Outstanding_Gap",
            "Purchase",
            "Gap Share %"
        ]
    ].to_string()
)
print("\n" + "=" * 70)
print("STAGE 10.17 — OPERATIONAL ATTRIBUTE INVESTIGATION")
print("=" * 70)

print("\nKey attributes of Collection-Under-LC gap records:")

print(
    lc_gap[
        [
            "Bill No.",
            "Bill Date",
            "Bill Type",
            "Currency",
            "Bill Value",
            "Bill Outstanding in FC",
            "Outstanding Gap",
            "Purchase Status",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Tenor Days",
            "Tenor Description",
            "Acceptance(Y/N)",
            "Maturity Date",
            "Contingent Liabilities",
            "PRODUCT_EXP",
            "TYPE_OF_EXP"
        ]
    ]
    .sort_values("Outstanding Gap", ascending=False)
    .to_string(index=False)
)
print("\n" + "=" * 70)
print("STAGE 10.18 — OUTSTANDING VS CONTINGENT LIABILITY RECONCILIATION")
print("=" * 70)

lc_gap_cl = lc_gap[
    [
        "Bill No.",
        "Bill Value",
        "Bill Outstanding in FC",
        "Contingent Liabilities",
        "Outstanding Gap"
    ]
].copy()

lc_gap_cl["Outstanding vs Contingent Gap"] = (
    lc_gap_cl["Bill Outstanding in FC"]
    - lc_gap_cl["Contingent Liabilities"]
)

print("\nRecord-level reconciliation:")

print(
    lc_gap_cl[
        [
            "Bill No.",
            "Bill Outstanding in FC",
            "Contingent Liabilities",
            "Outstanding vs Contingent Gap"
        ]
    ]
    .to_string(index=False)
)

print("\nReconciliation summary:")

print(
    lc_gap_cl[
        [
            "Bill Outstanding in FC",
            "Contingent Liabilities",
            "Outstanding vs Contingent Gap"
        ]
    ].sum()
)

print("\nRecords where Outstanding != Contingent Liabilities:")

print(
    (
        lc_gap_cl["Outstanding vs Contingent Gap"] != 0
    ).sum()
)

print("\nMaximum absolute difference:")

print(
    lc_gap_cl["Outstanding vs Contingent Gap"]
    .abs()
    .max()
)
print("\n" + "=" * 70)
print("STAGE 10.19 — THREE-WAY EXPOSURE RECONCILIATION")
print("=" * 70)

recon = lc_gap[
    [
        "Bill No.",
        "Bill Value",
        "Bill Outstanding in FC",
        "Contingent Liabilities"
    ]
].copy()

recon["Bill vs Outstanding"] = (
    recon["Bill Value"] - recon["Bill Outstanding in FC"]
)

recon["Bill vs Contingent"] = (
    recon["Bill Value"] - recon["Contingent Liabilities"]
)

recon["Outstanding vs Contingent"] = (
    recon["Bill Outstanding in FC"] - recon["Contingent Liabilities"]
)

def classify_reconciliation(row):

    bill = row["Bill Value"]
    outstanding = row["Bill Outstanding in FC"]
    contingent = row["Contingent Liabilities"]

    if (
        outstanding == contingent
        and bill == contingent
    ):
        return "All Three Equal"

    elif outstanding == contingent:
        return "Outstanding = Contingent"

    elif bill == contingent:
        return "Bill Value = Contingent"

    elif bill == outstanding:
        return "Bill Value = Outstanding"

    else:
        return "No Direct Equality"

recon["Reconciliation Pattern"] = recon.apply(
    classify_reconciliation,
    axis=1
)

print("\nReconciliation Pattern:")
print(
    recon["Reconciliation Pattern"]
    .value_counts()
)

print("\nDetailed Reconciliation:")
print(
    recon[
        [
            "Bill No.",
            "Bill Value",
            "Bill Outstanding in FC",
            "Contingent Liabilities",
            "Bill vs Outstanding",
            "Bill vs Contingent",
            "Outstanding vs Contingent",
            "Reconciliation Pattern"
        ]
    ].to_string(index=False)
)
print("\n" + "=" * 70)
print("STAGE 10.20 — PURCHASE-RELATED RECONCILIATION INVESTIGATION")
print("=" * 70)

purchase_gap = lc_gap[
    lc_gap["Total Purchase amount"] > 0
].copy()

purchase_gap["Purchase vs Bill Value"] = (
    purchase_gap["Bill Value"]
    - purchase_gap["Total Purchase amount"]
)

purchase_gap["Purchase vs Outstanding"] = (
    purchase_gap["Bill Outstanding in FC"]
    - purchase_gap["Total Purchase amount"]
)

purchase_gap["Contingent vs Unpurchased"] = (
    purchase_gap["Contingent Liabilities"]
    - purchase_gap["Un-purchased amount in FC"]
)

print("\nPurchase-related gap records:")

print(
    purchase_gap[
        [
            "Bill No.",
            "Bill Date",
            "Currency",
            "Bill Value",
            "Bill Outstanding in FC",
            "Contingent Liabilities",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Outstanding Gap",
            "Purchase vs Bill Value",
            "Purchase vs Outstanding",
            "Contingent vs Unpurchased"
        ]
    ].to_string(index=False)
)

print("\nPurchase-related totals:")

print(
    purchase_gap[
        [
            "Bill Value",
            "Bill Outstanding in FC",
            "Contingent Liabilities",
            "Total Purchase amount",
            "Un-purchased amount in FC",
            "Outstanding Gap"
        ]
    ].sum()
)
print("\n" + "=" * 70)
print("STAGE 11.1 — CUSTOMER EXPOSURE ANALYSIS")
print("=" * 70)

customer_exposure = (
    df.groupby(["Customer ID", "Applicant/Buyer Name"], dropna=False)
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchased=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

print("\nTop 15 Customers by Outstanding Exposure:")

print(
    customer_exposure.head(15).to_string()
)

print("\nCustomer Exposure Totals:")

print(
    customer_exposure[
        ["Bills", "Bill_Value", "Outstanding", "Purchased", "Unpurchased"]
    ].sum()
)
print("\n" + "=" * 70)
print("STAGE 11.2 — CUSTOMER CONCENTRATION")
print("=" * 70)

customer_rank = customer_exposure.copy()

customer_rank["Cumulative Outstanding"] = (
    customer_rank["Outstanding"].cumsum()
)

total_outstanding = customer_rank["Outstanding"].sum()

customer_rank["Cumulative Share %"] = (
    customer_rank["Cumulative Outstanding"]
    / total_outstanding
    * 100
)

print("\nTop 5 Customers:")

print(
    customer_rank.head(5)[
        [
            "Bills",
            "Bill_Value",
            "Outstanding",
            "Purchased",
            "Unpurchased",
            "Cumulative Share %"
        ]
    ].to_string()
)

print("\nTop 10 Customers:")

print(
    customer_rank.head(10)[
        [
            "Bills",
            "Bill_Value",
            "Outstanding",
            "Purchased",
            "Unpurchased",
            "Cumulative Share %"
        ]
    ].to_string()
)

print("\nTop 20 Customers:")

print(
    customer_rank.head(20)[
        [
            "Bills",
            "Bill_Value",
            "Outstanding",
            "Purchased",
            "Unpurchased",
            "Cumulative Share %"
        ]
    ].to_string()
)
print("\n" + "=" * 70)
print("STAGE 11.3 — EXPOSURE BY BUSINESS SEGMENT")
print("=" * 70)

segment_exposure = (
    df.groupby("Business Segment", dropna=False)
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchased=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

segment_exposure["Outstanding Share %"] = (
    segment_exposure["Outstanding"]
    / segment_exposure["Outstanding"].sum()
    * 100
)

print("\nExposure by Business Segment:")

print(
    segment_exposure.to_string()
)
print("\n" + "=" * 70)
print("STAGE 11.4 — EXPOSURE BY LINE OF BUSINESS")
print("=" * 70)

lob_exposure = (
    df.groupby("Line of Business", dropna=False)
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchased=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

lob_exposure["Outstanding Share %"] = (
    lob_exposure["Outstanding"]
    / lob_exposure["Outstanding"].sum()
    * 100
)

print("\nExposure by Line of Business:")

print(
    lob_exposure.to_string()
)
from pathlib import Path

home = Path.home()

files = list(home.rglob("LC_Portfolio_Analytics_Working.xlsx"))

currency_exposure = (
    df.groupby("Currency", dropna=False)
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchased=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

currency_exposure["Outstanding Share %"] = (
    currency_exposure["Outstanding"]
    / currency_exposure["Outstanding"].sum()
    * 100
)

country_exposure = (
    df.groupby("Applicant/Buyer's Country", dropna=False)
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchased=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

country_exposure["Outstanding Share %"] = (
    country_exposure["Outstanding"]
    / country_exposure["Outstanding"].sum()
    * 100
)

print("\n" + "=" * 70)
print("STAGE 11.6 — EXPOSURE BY APPLICANT/BUYER COUNTRY")
print("=" * 70)

print(country_exposure.head(20))
bank_exposure = (
    df.groupby("Issuing Bank", dropna=False)
      .agg(
          Bills=("Bill No.", "count"),
          Bill_Value=("Bill Value", "sum"),
          Outstanding=("Bill Outstanding in FC", "sum"),
          Purchased=("Total Purchase amount", "sum"),
          Unpurchased=("Un-purchased amount in FC", "sum")
      )
      .sort_values("Outstanding", ascending=False)
)

bank_exposure["Outstanding Share %"] = (
    bank_exposure["Outstanding"]
    / bank_exposure["Outstanding"].sum()
    * 100
)

print("\n" + "=" * 70)
print("STAGE 11.7 — EXPOSURE BY ISSUING BANK")
print("=" * 70)

print(bank_exposure.head(20))
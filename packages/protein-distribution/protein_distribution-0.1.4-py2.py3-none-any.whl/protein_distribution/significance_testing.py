"""
Testing of differences & multiple testing correction.

1. Independence of observations (a.k.a. no autocorrelation):
The observations/variables you include in your test are not related
(for example, multiple measurements of a single test subject are not independent,
while measurements of multiple different test subjects are independent).

=> measurement of multple different test sujects are indepenent.

2. Homogeneity of variance: the variance within each group being compared
is similar among all groups. If one group has much more variation than others,
it will limit the test’s effectiveness.

=> Before conducting the two-sample T-Test we need to find if the given data groups
have the same variance. If the ratio of the larger data groups to the small data
group is less than 4:1 then we can consider that the given data groups have equal variance.


3. Normality of data: the data follows a normal distribution (a.k.a. a bell curve).
This assumption applies only to quantitative data.

=> if 2 and 3 are not valid then we have to use nonparametric tests

Independent t-test:

p-values: * = 0.05, ** = 0.01, *** = 0.001

Multiple-testing correction:
https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html

2: groups testing (t-test)
- "sex", "smoking", "alcohol", "age_group"
3: groups testing (anova)
- "bmi_group"
no testing:
- ethnicities.
"""
from typing import Any, Dict

import numpy as np
import pandas as pd
import scipy.stats as stats

from protein_distribution.console import console
from protein_distribution.log import get_logger


logger = get_logger(__name__)


stratification_info = {
    "sex": {"groups": ["M", "F"], "colors": ["tab:blue", "tab:red"]},
    "smoking": {"groups": ["Y", "N"], "colors": ["tab:brown", "tab:gray"]},
    "alcohol": {"groups": ["Y", "N"], "colors": ["tab:olive", "tab:gray"]},
    "ethnicity": {
        "groups": ["caucasian", "african american", "hispanic"],
        "colors": ["tab:blue", "tab:orange", "tab:green"],
    },
    "age_group": {
        "groups": ["middle aged", "elderly"],
        "colors": ["#fdbb84", "#e34a33"],
    },
    "bmi_group": {
        "groups": ["normal weight", "overweight", "obese"],
        "colors": ["#d7b5d8", "#df65b0", "#ce1256"],
    },
}


def process_stratification_data(
    data: pd.DataFrame, stratification_key: str
) -> pd.DataFrame:
    """Process stratification data.

    existing groups and filtered groups:

    sex: [M, F, NR] -> [M, F]
    smoking [Y, N, NR] -> [Y, N]
    alcohol [Y, N, NR] -> [Y, N]
    ethnicity [caucasian, hispanic, african american, NR] -> [caucasian, african american, hispanic]
    age_group [adolescent, young, middle aged, elderly, NR] -> [middle aged, elderly]
    bmi_group [underweight, normal weight, overweight, obese, NR] -> [normal weight, overweight, obese]
    """

    if stratification_key not in stratification_info:
        raise ValueError(f"Unsupported stratification: {stratification_key}")

    # subset of abundance data for individual protein
    df_protein = data[~pd.isnull(data.value)]

    # filter out NR values
    df_protein = df_protein[~(df_protein[stratification_key] == "NR")]

    # filter out bmi_group: "underweight"
    if stratification_key == "bmi_group":
        df_protein = df_protein[~(df_protein[stratification_key] == "underweight")]
    # filter out age_group: "adolescent
    if stratification_key == "age_group":
        df_protein = df_protein[~(df_protein[stratification_key] == "adolescent")]

    # A minimum of 5 data points for every group required
    proteins_with_data = []
    groups = stratification_info[stratification_key]["groups"]
    for p in df_protein.protein.unique():
        if stratification_key == "ethnicity":
            include = False
        else:
            include = True

        for group in groups:
            df_group = df_protein[
                (df_protein.protein == p) & (df_protein[stratification_key] == group)
            ]

            if stratification_key == "ethnicity":
                # at least one group >= 10 subjects
                if len(df_group) >= 10:
                    include = True
                    break
            else:
                # all groups >= 10 subjects
                if len(df_group) < 10:
                    # console.print(f"Filtered protein '{p}' due to '{stratification_key}' = {group}")
                    include = False
                    break

        if include:
            proteins_with_data.append(p)

    # console.print("proteins with data", len(proteins_with_data) / len(df_protein.protein.unique()))

    # filter by proteins with sufficient data
    df_protein = df_protein[df_protein["protein"].isin(proteins_with_data)]

    return df_protein


def equality_of_variance(dfs: Dict[str, pd.DataFrame]) -> Dict:
    """Test equality of variance of groups.

    can be tested using Levene’s, Bartlett’s, or Brown-Forsythe test
    """

    variances = {group: np.var(df.value) for group, df in dfs.items()}
    variances_values = variances.values()
    var_min = min(variances_values)
    var_max = max(variances_values)
    var_ratio = var_max / var_min

    # Test that ratio < 4:1
    var_equal: bool = var_ratio <= 4.0
    # if not var_equal:
    #    logger.error(f"Variance ratio > 4:1, {var_ratio:.2f}")

    return {
        "variance ratio": var_ratio,
        "variance equal": var_equal,
    }


def significance_for_pvalue(pvalue: float) -> str:
    """Significance marker for pvalue."""
    if pvalue <= 0.001:
        significance = "***"
    elif pvalue <= 0.01:
        significance = "**"
    elif pvalue <= 0.05:
        significance = "*"
    else:
        significance = " "
    return significance


def two_sample_ttest(dfs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Calculate two-sample t-test."""
    # perform testing of variance
    var_results = equality_of_variance(dfs_ttest)

    # group data
    data = [df.value.values for df in dfs.values()]

    # Perform the two sample t-test with equal variances
    t_results = stats.ttest_ind(a=data[0], b=data[1], equal_var=True)

    pvalue = t_results.pvalue
    significance = significance_for_pvalue(pvalue)
    # console.print(f"p-value={t_results.pvalue}, df={t_results.df}, u significance: '{significance}'")
    return {
        "method": "t-test",
        "pvalue": pvalue,
        "df": t_results.df,
        "sig": significance,
        **var_results,
    }


def two_sample_mannwitneyu(dfs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Calculate two-sample Mann-Whitney test (unpaired).

    The most popular alternative is the Mann-Whitney test, which is done with
    the stats::wilcox.test function in R
    (http://stat.ethz.ch/R-manual/R-devel/library/stats/html/wilcox.test.html).

    The Wilcoxon signed-rank test tests the null hypothesis that two related paired
    samples come from the same distribution. In particular, it tests whether the
    distribution of the differences x - y is symmetric about zero. It is a non-parametric
    version of the paired T-test.
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
    """
    # group data
    data = [df.value.values for df in dfs.values()]

    # Perform the two sample t-test with equal variances
    test_results = stats.mannwhitneyu(x=data[0], y=data[1])

    pvalue = test_results.pvalue
    significance = significance_for_pvalue(pvalue)
    # console.print(f"p-value={t_results.pvalue}, df={t_results.df}, u significance: '{significance}'")
    return {
        "method": "Mann-Whitney",
        "pvalue": pvalue,
        "sig": significance,
    }


def kruskal_wallis(dfs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Kruskal Wallis significance test of data.

    A Kruskal-Wallis test is used to determine whether or not there is a
    statistically significant difference between the medians of three or
    more independent groups.

    This test is the nonparametric equivalent of the one-way ANOVA and is typically
    used when the normality assumption is violated.

    The Kruskal-Wallis test does not assume normality in the data and is much less
    sensitive to outliers than the one-way ANOVA.

    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html

    :return:
    """
    # group data
    data = [df.value.values for df in dfs.values()]

    # Perform kruskall wallis
    test_results = stats.kruskal(*data)

    pvalue = test_results.pvalue
    significance = significance_for_pvalue(pvalue)

    return {
        "method": "Kruskal-Wallis",
        "pvalue": pvalue,
        "sig": significance,
    }


if __name__ == "__main__":
    from protein_distribution import DATA_MERGED_XLSX, DATA_XLSX, RESULTS_DIR
    from protein_distribution.protein_info import get_protein_categories, get_proteins

    df_abundance = pd.read_excel(DATA_XLSX, sheet_name="Abundance")
    del df_abundance["comments"]
    df_abundance["sid"] = df_abundance["study"] + "_" + df_abundance["source"]

    proteins = get_proteins(df_abundance, uniprot=True)
    protein_categories = get_protein_categories(proteins)

    df_individual_data = pd.read_excel(DATA_MERGED_XLSX, sheet_name="individual_data")

    ttest_results = []
    for category in ["cyp", "ugt", "slc", "abc"]:
        df_category = df_individual_data[
            df_individual_data.protein.isin(protein_categories[category])
        ]

        for stratification_key in [
            "sex",
            "smoking",
            "alcohol",
            "ethnicity",
            "age_group",
            "bmi_group",
        ]:
            groups = stratification_info[stratification_key]["groups"]
            df_proteins = process_stratification_data(
                df_category, stratification_key=stratification_key
            )
            # print(df_proteins)

            proteins = df_proteins.protein.unique()
            for protein_id in proteins:
                dfs_ttest = {}
                for group in groups:
                    # console.print(f"protein: {protein_id}, key: {stratification_key}, group: {group}")
                    df = df_proteins[
                        (df_proteins.protein == protein_id)
                        & (df_proteins[stratification_key] == group)
                    ]
                    dfs_ttest[group] = df

                # t-tests/wilcoxon/Mann-Whitney
                if stratification_key in ["sex", "alcohol", "age_group", "smoking"]:
                    # test_results = two_sample_ttest(dfs_ttest)
                    test_results = two_sample_mannwitneyu(dfs_ttest)

                # anova (Kruskall Wallis)
                elif stratification_key in ["bmi_group"]:
                    test_results = kruskal_wallis(dfs_ttest)

                elif stratification_key in ["ethnicity"]:
                    # not tested
                    continue

                ttest_results.append(
                    {
                        "category": category,
                        "protein": protein_id,
                        "variable": stratification_key,
                        **test_results,
                    }
                )

    df_ttest = pd.DataFrame(ttest_results)
    df_ttest.sort_values(by="pvalue", inplace=True)

    # multiple testing correction
    from statsmodels.stats.multitest import multipletests

    pvals = df_ttest.pvalue.values
    (
        reject,
        pvals_corrected,
        _,
        _,
    ) = multipletests(
        pvals,
        alpha=0.05,  # FWER, family-wise error rate, e.g. 0.1
        method="fdr_bh",  # hs,
        maxiter=1,
        is_sorted=False,
        returnsorted=False,
    )
    df_ttest["pvalue corrected"] = pvals_corrected
    df_ttest["sig corrected"] = [
        significance_for_pvalue(pval) for pval in pvals_corrected
    ]

    console.rule(style="white")
    console.print(df_ttest.to_string())
    console.rule(style="white")

    table_significance = RESULTS_DIR / "table_stratification.xlsx"
    with pd.ExcelWriter(table_significance) as writer:
        for category in ["cyp", "ugt", "slc", "abc"]:
            df = df_ttest[df_ttest.category == category]
            df.to_excel(writer, sheet_name=category, index=False)

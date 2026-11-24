# Enterprise AI Incident Intelligence Platform

## Exploratory Data Analysis (EDA) --- Project Notes

**Purpose:** This document records the EDA performed on the UCI Incident
Management Process Enriched Event Log dataset. It explains the code, why
each analysis was performed, the findings, and the decisions made.

> **Project context:** Predicting incident priority is one ML component
> of the larger Enterprise AI Incident Intelligence Platform. The
> broader platform is intended to combine ML, retrieval-augmented
> generation (RAG), AI agents, MCP tools, an API/backend, and a user
> interface.

------------------------------------------------------------------------

## 1. Overall project goal and current ML task

The overall project aims to build an intelligent incident-management
assistant that can help support teams understand incidents, retrieve
relevant historical cases and documentation, investigate possible
causes, and recommend next steps.

The current ML task is narrower:

**Predict an incident's priority using information available when the
incident is created.**

The target column is `priority`.

We plan to compare two models:

-   **Model A:** Uses valid creation-time features, including `impact`
    and `urgency`.
-   **Model B:** Uses the same valid creation-time features, but
    excludes `impact` and `urgency`.

This comparison will help us understand how much predictive information
comes from the impact/urgency relationship and whether other incident
details provide useful signal.

------------------------------------------------------------------------

## 2. Dataset overview

Dataset: **UCI Incident Management Process Enriched Event Log**

The original dataset contains approximately:

-   141,712 event rows
-   24,918 distinct incident numbers
-   36 columns

### Important: one row is an event, not necessarily one incident

The same incident number appears in multiple rows because the dataset
records changes and events during an incident's lifecycle.

For example, an incident may have one row when first recorded, another
when its priority changes, and further rows as it is assigned, updated,
resolved, or closed.

### Initial inspection

``` python
df.shape
```

`shape` returns a tuple containing the number of rows and columns.

``` python
df.columns.tolist()
```

Displays the column names as a Python list.

``` python
df.info()
```

Shows the number of non-null values, data types, and memory usage for
each column.

**Why we did this:** Before analyzing the data, we needed to understand
its size, structure, available attributes, and data types.

------------------------------------------------------------------------

## 3. Repeated incident records

### Code

``` python
df["number"].value_counts().describe()
```

### What the code does

-   `df["number"]` selects the incident-number column as a Series.
-   `value_counts()` counts how many rows each incident number has.
-   `describe()` summarizes those counts.

### Findings

  Statistic                         Value
  ------------------------------ --------
  Distinct incidents               24,918
  Mean event rows per incident      5.687
  Standard deviation                3.678
  Minimum                               2
  Median                                5
  Maximum                              58

**Interpretation:** Each incident has multiple event rows. Training
directly on all event rows for an initial-priority prediction task could
cause the same incident to appear repeatedly and could expose the model
to later lifecycle information.

------------------------------------------------------------------------

## 4. Investigating priority changes

We wanted to determine whether an incident's priority changes during its
lifecycle.

### Code

``` python
priority_changes = (
    df.groupby("number")["priority"].nunique()
)

display(priority_changes.value_counts())
```

### Concepts

-   `groupby("number")`: groups rows belonging to the same incident.
-   `["priority"]`: selects the priority column within each group.
-   `nunique()`: counts the distinct priority values for each incident.
-   `value_counts()`: counts how many incidents have each
    distinct-priority count.

### Findings

  Number of distinct priority values     Number of incidents
  ------------------------------------ ---------------------
  1                                                   24,535
  2                                                      351
  3                                                       32

Most incidents had one recorded priority, while a smaller number had two
or three distinct priority values.

### Inspecting incidents with changed priorities

``` python
changed_incidents = priority_changes[
    priority_changes > 1
]

changed_history = df[
    df["number"].isin(changed_incidents.index)
]

priority_timeline = changed_history[
    ["number", "priority", "opened_at", "sys_updated_at"]
]

display(priority_timeline.head(20))
```

`priority_changes` is a Series indexed by incident number. Therefore, we
use `changed_incidents.index` to get the incident numbers.

`isin()` checks whether each value in `df["number"]` appears in the
supplied collection.

### Why this matters

Our target is the priority at the prediction point, which is incident
creation. A priority change later in the lifecycle should not
automatically replace the initial target.

**Important limitation:** The earliest recorded event is not necessarily
the exact creation event. This must be validated before describing its
priority as definitively the priority at creation.

------------------------------------------------------------------------

## 5. Creating one row per incident

We selected the earliest recorded event for each incident.

### Code

``` python
first_records = (
    df.sort_values("sys_updated_at")
      .drop_duplicates(subset="number", keep="first")
      .reset_index(drop=True)
)
```

### Explanation

-   `sort_values("sys_updated_at")`: sorts events by update time.
-   `drop_duplicates(subset="number", keep="first")`: keeps the earliest
    row for each incident number after sorting.
-   `reset_index(drop=True)`: creates a fresh integer index and discards
    the previous index.

### Why use `drop_duplicates()`?

`groupby().first()` can select the first non-null value independently
for each column. That can potentially combine values from different
event rows. `drop_duplicates()` keeps one complete original row
together.

### Validation

``` python
first_records.shape
```

``` python
first_records["number"].nunique()
```

``` python
first_records["number"].duplicated().sum()
```

### Findings

-   Rows: 24,918
-   Unique incident numbers: 24,918
-   Duplicate incident numbers: 0

We now have one recorded row per incident.

**Caution:** This is the earliest recorded event per incident, not
automatically a verified snapshot of all fields at the exact opening
time.

------------------------------------------------------------------------

## 6. Target variable: priority

### Code

``` python
display(first_records["priority"].value_counts())
```

### Findings

  Priority          Count
  -------------- --------
  3 - Moderate     23,674
  4 - Low             741
  2 - High            317
  1 - Critical        186

To calculate percentages:

``` python
display(
    first_records["priority"].value_counts(normalize=True) * 100
)
```

After the timestamp filtering described later, the percentages were:

  Priority         Percentage
  -------------- ------------
  3 - Moderate         95.01%
  4 - Low               2.97%
  2 - High              1.27%
  1 - Critical          0.75%

### Class imbalance

The target is severely imbalanced: approximately 95% of incidents are
Moderate.

A model that predicts Moderate for every incident could achieve roughly
95% accuracy while failing to identify Critical, High, and Low
incidents.

Therefore, accuracy alone is not enough. We plan to evaluate:

-   Precision
-   Recall
-   F1-score
-   Macro F1-score
-   Confusion matrix

Macro F1 is especially useful to assess performance across all classes
rather than allowing the majority class to dominate the summary.

------------------------------------------------------------------------

## 7. Relationship between impact, urgency, and priority

We investigated whether impact and urgency are associated with priority.

### Code

``` python
pd.crosstab(
    [first_records["impact"], first_records["urgency"]],
    first_records["priority"]
)
```

### What `crosstab()` does

`pd.crosstab()` creates a frequency table for categorical variables.

In this analysis:

-   Rows: combinations of `impact` and `urgency`
-   Columns: `priority`
-   Cell values: number of incidents in each combination

### Findings

Impact and urgency showed a strong relationship with priority. For
example, high impact combined with high urgency was associated with
Critical priority, while medium impact and medium urgency was
predominantly associated with Moderate priority.

### Why compare two models?

Impact and urgency may encode much of the organization's ITSM priority
matrix. We want to test:

-   How well a model performs when it has these two attributes.
-   Whether other incident information can predict priority without
    them.

This is why we plan Model A and Model B.

------------------------------------------------------------------------

## 8. Investigating `u_priority_confirmation`

The dataset documentation describes this as an indicator of whether the
priority field was double-checked.

### Value counts

``` python
display(
    clean_records["u_priority_confirmation"].value_counts()
)
```

Findings:

  Value      Count
  ------- --------
  False     24,821
  True          97

### Relationship with priority

``` python
pd.crosstab(
    clean_records["u_priority_confirmation"],
    clean_records["priority"]
)
```

Both True and False appeared across priority classes. This indicates
that the confirmation flag does not itself determine the priority.

**Caution:** Its meaning does not establish when it became available. We
must verify its timing before including it in a creation-time model.

------------------------------------------------------------------------

## 9. Timestamp conversion and investigation

The `opened_at` and `sys_updated_at` columns were converted from strings
into datetime values.

``` python
df["opened_at"] = pd.to_datetime(
    df["opened_at"],
    dayfirst=True
)

df["sys_updated_at"] = pd.to_datetime(
    df["sys_updated_at"],
    dayfirst=True
)
```

### Why convert timestamps?

Datetime values allow us to compare timestamps, subtract them, extract
hours, and perform time-based analysis.

### Calculate the time difference

``` python
first_records["time_difference"] = (
    first_records["sys_updated_at"]
    - first_records["opened_at"]
)

display(first_records["time_difference"].describe())
```

The summary showed five negative time differences: for those incidents,
the earliest recorded `sys_updated_at` was earlier than `opened_at`.

### Inspect negative records

``` python
negative_records = first_records[
    first_records["time_difference"] < pd.Timedelta(0)
]

display(
    negative_records[
        [
            "number",
            "opened_at",
            "sys_updated_at",
            "time_difference",
            "priority"
        ]
    ].head(10)
)
```

### Create a separate cleaned dataset

``` python
clean_records = first_records[
    first_records["time_difference"] >= pd.Timedelta(0)
].copy()
```

Findings:

  Description           Count
  ------------------ --------
  Before filtering     24,918
  After filtering      24,913
  Removed                   5

Only approximately 0.02% of records were removed.

**Important:** We identified timestamp anomalies, but did not establish
their cause. We should not claim that they were definitely corrupted or
caused by time zones. The original `first_records` DataFrame was
retained, and the filtered records were placed in a separate copy.

------------------------------------------------------------------------

## 10. Missing values, empty strings, and placeholders

### Check pandas null values

``` python
missing_values = clean_records.isnull().sum()

missing_values = missing_values[
    missing_values > 0
].sort_values(ascending=False)

display(missing_values)
```

The result was an empty Series: no pandas null values were detected.

### Check empty strings

``` python
empty_counts = (clean_records == "").sum()

display(empty_counts[empty_counts > 0])
```

The result was also empty: no empty strings were detected.

### Important distinction: `?`

The dataset uses `?` as a placeholder for unknown or unavailable
information.

`isnull()` does not treat the literal string `"?"` as a missing value.
Therefore, the null and empty-string checks do not mean that every field
is known.

We investigated these placeholders using `value_counts()` and retained
them as explicit unknown categories during EDA rather than deleting
entire incidents.

------------------------------------------------------------------------

## 11. Identifying constant columns

### Code

``` python
display(clean_records.nunique().sort_values())
```

`nunique()` counts the number of distinct values in each column.

We found that `reopen_count` had only one distinct value.

### Identify constant columns

``` python
constant_columns = clean_records.nunique()

constant_columns = constant_columns[
    constant_columns == 1
]

display(constant_columns)
```

### Remove the constant column

``` python
clean_records = clean_records.drop(
    columns=["reopen_count"]
)
```

**Why?** A feature with the same value for every record cannot
distinguish between incidents. It provides no useful variation for the
model.

------------------------------------------------------------------------

## 12. Feature exploration

The following analyses investigated potential creation-time attributes.
A relationship with priority does not, by itself, prove that a feature
is available at creation or suitable for prediction.

### 12.1 `opened_at` and `opened_hour`

Extract the hour:

``` python
clean_records["opened_hour"] = (
    clean_records["opened_at"].dt.hour
)
```

Count incidents by hour:

``` python
display(
    clean_records["opened_hour"].value_counts().sort_index()
)
```

Calculate priority percentages by hour:

``` python
hour_priority_percentage = pd.crosstab(
    clean_records["opened_hour"],
    clean_records["priority"],
    normalize="index"
) * 100

display(hour_priority_percentage.round(2))
```

Plot the percentages:

``` python
hour_priority_percentage.plot(
    kind="line",
    figsize=(12, 6),
    marker="o"
)

plt.xlabel("Opened Hour")
plt.ylabel("Percentage of Incidents")
plt.title("Priority Distribution by Opening Hour")
plt.xticks(range(24))
plt.grid(True)
plt.show()
```

**Findings:**

-   Moderate priority dominated throughout the day.
-   Low-priority incidents showed a noticeable percentage increase
    around 9 PM and 10 PM.
-   Those hours had smaller sample sizes.

**Decision:** Keep `opened_hour` as a candidate feature. Do not infer
that opening time causes priority from this analysis.

### 12.2 `contact_type`

Count values:

``` python
display(
    clean_records["contact_type"].value_counts()
)
```

Calculate priority percentages within each contact type:

``` python
pd.crosstab(
    clean_records["contact_type"],
    clean_records["priority"],
    normalize="index"
) * 100
```

Findings:

-   Phone was the dominant contact type.
-   Email, self-service, IVR, and direct opening had much smaller sample
    sizes.
-   Percentages for very small groups are unstable and should be
    interpreted cautiously.

**Decision:** Keep `contact_type` as a candidate feature.

### 12.3 `category`

Count distinct categories:

``` python
clean_records["category"].nunique()
```

Count category frequencies:

``` python
display(
    clean_records["category"].value_counts()
)
```

Calculate priority percentages:

``` python
category_priority = pd.crosstab(
    clean_records["category"],
    clean_records["priority"],
    normalize="index"
) * 100

display(category_priority.round(2))
```

Findings:

-   There were 58 unique values.
-   Priority distributions differed between categories.
-   Some categories had very few incidents, so their percentages were
    based on tiny samples.

For example, a category with six incidents and one Critical incident has
a 16.67% Critical rate, but that percentage is based on only one
Critical incident.

**Decision:** Keep `category` as a candidate feature. Investigate rare
categories during preprocessing.

### 12.4 `subcategory`

Count unique subcategories:

``` python
clean_records["subcategory"].nunique()
```

Display the 20 most frequent:

``` python
display(
    clean_records["subcategory"].value_counts().head(20)
)
```

Calculate priority percentages:

``` python
subcategory_priority = pd.crosstab(
    clean_records["subcategory"],
    clean_records["priority"],
    normalize="index"
) * 100
```

Select the 20 most frequent subcategories:

``` python
top_subcategories = (
    clean_records["subcategory"]
    .value_counts()
    .head(20)
    .index
)

display(
    subcategory_priority.loc[top_subcategories].round(2)
)
```

**Important Pandas learning:** `head(20)` on a crosstab returns the
first 20 index-sorted rows, not necessarily the 20 most frequent values.
We first use `value_counts().head(20)` to find the most frequent
categories, then use `.loc[]` to select those rows.

### Check the relationship between category and subcategory

``` python
subcategory_category = (
    clean_records.groupby("subcategory")["category"].nunique()
)

display(subcategory_category.value_counts())
```

Explanation:

-   `groupby("subcategory")` groups incidents by subcategory.
-   `["category"]` selects the category column within each group.
-   `nunique()` counts distinct categories associated with each
    subcategory.
-   `value_counts()` counts how many subcategories have each
    distinct-category count.

We found that many subcategories appeared under one category, but some
appeared under multiple categories. For example, Subcategory 174
appeared across many categories.

**Conclusion:** Subcategory does not uniquely determine category. Both
may contain useful information.

**Decision:** Keep both as candidate features until model evaluation.

### 12.5 `location`

Count distinct locations:

``` python
clean_records["location"].nunique()
```

Display the 20 most frequent locations:

``` python
display(
    clean_records["location"].value_counts().head(20)
)
```

Create count and percentage tables:

``` python
location_priority_counts = pd.crosstab(
    clean_records["location"],
    clean_records["priority"]
)

location_priority_percentage = pd.crosstab(
    clean_records["location"],
    clean_records["priority"],
    normalize="index"
) * 100

location_analysis = pd.concat(
    {
        "Count": location_priority_counts,
        "Percentage": location_priority_percentage
    },
    axis=1
)

display(location_analysis.round(2).head(20))
```

**Why combine counts and percentages?** Percentages show the
distribution, while counts show how much evidence supports that
distribution.

A location with 100% Critical priority based on two incidents should not
be treated as a reliable pattern. A location with thousands of incidents
provides a more substantial sample.

**Decision:** Keep `location` as a candidate feature, subject to timing
verification.

### 12.6 `u_symptom`

Count distinct values and inspect the most frequent:

``` python
clean_records["u_symptom"].nunique()
```

``` python
display(
    clean_records["u_symptom"].value_counts().head(20)
)
```

Create count and percentage tables:

``` python
symptom_priority_counts = pd.crosstab(
    clean_records["u_symptom"],
    clean_records["priority"]
)

symptom_priority_percentage = pd.crosstab(
    clean_records["u_symptom"],
    clean_records["priority"],
    normalize="index"
) * 100

symptom_analysis = pd.concat(
    {
        "Count": symptom_priority_counts,
        "Percentage": symptom_priority_percentage
    },
    axis=1
)

display(symptom_analysis.head(20).round(2))
```

Findings:

-   There were 501 unique values.
-   `?` appeared 5,744 times, approximately 23% of the dataset.
-   Some symptom values had relatively few incidents.

**Decision:** Keep `u_symptom` as a candidate feature, but plan to
investigate rare-category handling and encoding.

------------------------------------------------------------------------

## 13. Attributes with very little known information

We inspected `cmdb_ci`, `vendor`, and `caused_by`.

### `cmdb_ci`

``` python
display(
    clean_records["cmdb_ci"].value_counts().head(20)
)
```

Findings:

-   `?`: 24,862
-   Known values: 51 records in total

`cmdb_ci` refers to a configuration item, such as an application,
server, or network component.

**Decision:** Exclude from the initial feature set because almost all
records are unknown.

### `vendor`

``` python
display(
    clean_records["vendor"].value_counts()
)
```

Findings:

-   `?`: 24,897
-   `Vendor 1`: 10
-   `code 8s`: 6

Only 16 records had a non-placeholder value.

**Decision:** Exclude from the initial feature set because it has almost
no usable coverage.

### `caused_by`

``` python
display(
    clean_records["caused_by"].value_counts()
)
```

Findings:

-   `?`: 24,911
-   Two change IDs had values.

**Decision:** Exclude from the initial feature set because only two
records had a known value.

We retained the incident rows; we did not delete incidents because these
individual columns were mostly unknown.

------------------------------------------------------------------------

## 14. Investigating `caller_id` and `opened_by`

These attributes represent different roles:

-   `caller_id`: the person who reported the incident.
-   `opened_by`: the account that opened or created the incident record.

### 14.1 `caller_id`

Inspect frequent callers:

``` python
display(
    clean_records["caller_id"].value_counts().head(20)
)
```

Check priority counts for the most frequent callers:

``` python
caller_priority = pd.crosstab(
    clean_records["caller_id"],
    clean_records["priority"]
)

caller_priority["total"] = caller_priority.sum(axis=1)

display(
    caller_priority.sort_values(
        "total", ascending=False
    ).head(20)
)
```

Examples from the analysis:

-   Caller 1904: 430 Moderate incidents out of 438.
-   Caller 290: 136 Low incidents out of 257.
-   Caller 4514: 76 High incidents out of 130.

**Interpretation:** Priority distributions differed across callers.

**Risk:** There are thousands of caller IDs. A model may memorize
individual identities instead of learning general patterns, and new
callers may not exist in the training data.

**Decision:** Keep `caller_id` as an experimental feature. Compare
performance with and without it and evaluate generalization.

### 14.2 `opened_by`

Inspect frequent creators:

``` python
display(
    clean_records["opened_by"].value_counts().head(20)
)
```

Check priority counts:

``` python
opened_by_priority = pd.crosstab(
    clean_records["opened_by"],
    clean_records["priority"]
)

opened_by_priority["total"] = opened_by_priority.sum(axis=1)

display(
    opened_by_priority.sort_values(
        "total", ascending=False
    ).head(20)
)
```

Examples:

-   Opened by 17 created 7,214 incidents, most of which were Moderate.
-   Opened by 131 had 380 Low incidents out of 1,236.

**Decision:** Keep `opened_by` as an experimental feature, subject to
timing verification and evaluation of generalization.

------------------------------------------------------------------------

## 15. Post-creation attributes and data leakage

We identified attributes that describe incident handling or resolution
rather than the initial incident report.

  -----------------------------------------------------------------------
  Attribute               Meaning                 Initial prediction
                                                  decision
  ----------------------- ----------------------- -----------------------
  `assignment_group`      Team handling the       Exclude until timing is
                          incident                verified

  `assigned_to`           Person assigned to      Exclude
                          handle it               

  `resolved_by`           Person who resolved it  Exclude

  `reassignment_count`    Number of reassignments Exclude

  `sys_mod_count`         Number of modifications Exclude

  `closed_code`           Closure information     Exclude

  `resolved_at`           Resolution timestamp    Exclude

  `closed_at`             Closure timestamp       Exclude
  -----------------------------------------------------------------------

### Why?

Our prediction point is incident creation.

A simplified lifecycle:

1.  Incident is created.
2.  Initial priority is assigned.
3.  A support team or technician handles it.
4.  The incident is resolved and closed.

Using information from later stages to predict the initial priority
would introduce **data leakage**.

A feature can be associated with priority but still be invalid for the
intended prediction task if it is not available at prediction time.

**Nuance:** Some organizations may assign a group immediately during
creation. We should verify the actual timing of `assignment_group`
rather than assume it is always post-creation. Until verified, it
remains excluded.

------------------------------------------------------------------------

## 16. Current feature decisions

These are preliminary decisions. They are not a final approved feature
list until feature timing is verified.

### Candidate features

  Feature          Reason
  ---------------- -------------------------------------------
  `impact`         Describes extent of business impact
  `urgency`        Describes how quickly attention is needed
  `category`       Incident classification
  `subcategory`    More detailed incident classification
  `contact_type`   How the incident was reported
  `u_symptom`      Reported symptom information
  `location`       Incident location
  `opened_hour`    Time of incident opening
  `caller_id`      Experimental; high cardinality
  `opened_by`      Experimental; creator identity

### Excluded or not currently selected

  -----------------------------------------------------------------------
  Feature                             Reason
  ----------------------------------- -----------------------------------
  `number`                            Incident identifier

  `priority`                          Target variable

  `reopen_count`                      Constant column

  `cmdb_ci`                           Almost entirely unknown

  `vendor`                            Almost entirely unknown

  `caused_by`                         Almost entirely unknown

  `sys_created_by`                    Approximately 46% unknown; overlap
                                      with creator information needs
                                      investigation

  `sys_created_at`                    Approximately 46% invalid (`?`)

  `time_difference`                   Derived for timestamp
                                      investigation, not a creation-time
                                      feature

  `sys_updated_at`                    Update timestamp, not necessarily
                                      available at creation

  `assigned_to`                       Assignment/handling information

  `resolved_by`                       Resolution information

  `assignment_group`                  Excluded until timing is verified
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 17. Pandas functions practiced

  -----------------------------------------------------------------------
  Function or syntax                  Purpose
  ----------------------------------- -----------------------------------
  `.shape`                            Returns number of rows and columns

  `.info()`                           Shows data types and column
                                      information

  `.columns`                          Accesses column names

  `.value_counts()`                   Counts occurrences of each value

  `.describe()`                       Produces a statistical summary

  `.groupby()`                        Groups rows by one or more columns

  `.nunique()`                        Counts distinct values

  `pd.crosstab()`                     Creates a frequency table for
                                      categorical variables

  `normalize="index"`                 Converts crosstab rows into
                                      proportions

  `.isin()`                           Checks membership in a collection

  `.sort_values()`                    Sorts values or rows

  `.drop_duplicates()`                Removes duplicate rows based on
                                      selected columns

  `.reset_index()`                    Resets the index

  `.isnull()`                         Detects pandas null values

  `.sum()`                            Sums values; can count True values
                                      in Boolean results

  `.drop()`                           Removes selected rows or columns

  `pd.concat()`                       Combines Series or DataFrames

  `.head()`                           Returns the first rows

  `.round()`                          Rounds numerical values

  `pd.to_datetime()`                  Converts values into datetime

  `.dt.hour`                          Extracts the hour from a datetime
                                      column

  `.loc[]`                            Selects rows or columns by label
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 18. Practical EDA coding assessment

Use the `clean_records` DataFrame. Try to solve these without looking up
the answers first.

### Level 1 --- Basic Pandas

1.  Display the number of rows and columns in `clean_records`.
2.  Display the 10 most frequent values in `category`.
3.  Find the number of unique values in `subcategory`.
4.  Display the priority distribution as percentages rather than counts.

### Level 2 --- Grouping and counting

5.  Group the dataset by `priority` and calculate how many unique
    callers exist in each priority group.
6.  Find how many distinct priorities each incident number has.
7.  Count how many incidents have exactly two distinct priority values.

### Level 3 --- Crosstab

8.  Create a table showing the count of incidents for each combination
    of `impact` and `urgency`.
9.  Create a table showing the percentage distribution of priority for
    each `contact_type`.
10. Create a crosstab between `category` and `priority`, displaying only
    the 10 most frequent categories.

### Level 4 --- Combining concepts

11. Create a table containing both counts and percentages of priority
    for each location.
12. Find the 15 most frequent callers and display their priority counts.
13. Identify all columns that contain exactly one unique value.
14. Find all records where `time_difference` is negative.
15. Extract the opening hour and find the hour with the highest number
    of incidents.

------------------------------------------------------------------------

## 19. Interview explanation of the EDA

A concise way to explain this work:

"I started by understanding the structure of the incident event log.
Since each incident had multiple event records, I investigated repeated
incident IDs and their priority histories.

I then created a one-record-per-incident dataset using the earliest
recorded event, while recognizing that the earliest event is not
necessarily the exact creation timestamp.

Next, I examined the target distribution and discovered severe class
imbalance, with approximately 95% of incidents belonging to Moderate
priority.

I investigated relationships between impact, urgency, category,
subcategory, and other attributes using frequency distributions and
crosstab analysis.

I also performed data-quality checks, identified timestamp anomalies,
removed five records from the analytical dataset, and identified
constant and mostly unknown columns.

Finally, I separated potential creation-time features from post-creation
attributes to reduce the risk of data leakage.

The next stage is to validate feature availability, preprocess the
selected features, and compare two classification models with and
without impact and urgency."

------------------------------------------------------------------------

## 20. Key lessons from this EDA

EDA is not just counting values or generating charts. It helps answer:

1.  What does the dataset contain?
2.  Is the data reliable?
3.  What patterns exist?
4.  Which features might be useful?
5.  Which columns should be excluded?
6.  Are we accidentally using future information?
7.  What limitations should be considered before model training?

**Current status:** Initial EDA and preliminary feature investigation
are complete. Feature timing validation, final feature selection,
preprocessing, and model training are still pending.

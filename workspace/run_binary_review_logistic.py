#!/usr/bin/env python3
import csv
import json
import math
import random
from pathlib import Path


ROOT = Path("/Users/eveyhuang/Documents/NICO/human-AI-proposal")
TABLES_DIR = ROOT / "results" / "tables" / "rephrased"
FIGURES_DIR = ROOT / "results" / "figures" / "rephrased"
REVIEW_DIR = ROOT / "data" / "reviews" / "ai_reviews"


def norm(text):
    return str(text).strip().lower()


def slugify(text):
    return (
        norm(text)
        .replace(" & ", "_and_")
        .replace("&", "and")
        .replace("/", "_")
        .replace(" ", "_")
    )


def parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_float(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        val = float(text)
    except ValueError:
        return None
    if math.isnan(val) or math.isinf(val):
        return None
    return val


def load_csv_rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def merge_feature_rows():
    style_rows = load_csv_rows(TABLES_DIR / "style_features.csv")
    nn_rows = load_csv_rows(TABLES_DIR / "nn_distances.csv")
    centroid_rows = load_csv_rows(TABLES_DIR / "centroid_distances.csv")
    novelty_rows = load_csv_rows(TABLES_DIR / "novelty_scores_from_literature.csv")

    style_fields = [
        field
        for field in style_rows[0].keys()
        if field not in {"title", "group", "is_ai"}
    ]

    feature_map = {}

    for row in style_rows:
        title_norm = norm(row["title"])
        feature_map[title_norm] = {
            "title": row["title"],
            "title_norm": title_norm,
            "group": row.get("group", ""),
        }
        for field in style_fields:
            feature_map[title_norm][field] = parse_float(row.get(field))

    for row in nn_rows:
        title_norm = norm(row["title"])
        if title_norm not in feature_map:
            continue
        feature_map[title_norm]["nn_dist"] = parse_float(row.get("nn_dist"))
        feature_map[title_norm]["is_nn_outlier"] = 1.0 if parse_bool(row.get("is_outlier")) else 0.0

    for row in centroid_rows:
        title_norm = norm(row["title"])
        if title_norm not in feature_map:
            continue
        feature_map[title_norm]["centroid_dist"] = parse_float(row.get("centroid_dist"))

    for row in novelty_rows:
        title_norm = norm(row["title"])
        if title_norm not in feature_map:
            continue
        feature_map[title_norm]["raw_novelty"] = parse_float(row.get("raw_novelty"))
        feature_map[title_norm]["novelty_z"] = parse_float(row.get("novelty_z"))
        feature_map[title_norm]["is_literature_outlier"] = (
            1.0 if parse_bool(row.get("is_most_novel_raw")) else 0.0
        )

    feature_names = style_fields + [
        "nn_dist",
        "centroid_dist",
        "raw_novelty",
        "novelty_z",
        "is_nn_outlier",
        "is_literature_outlier",
    ]
    return feature_map, feature_names


def load_review_rows(feature_map):
    review_files = sorted(REVIEW_DIR.glob("ai_reviews_rephrased_*.json"))
    if not review_files:
        raise FileNotFoundError(f"No rephrased review JSON found in {REVIEW_DIR}")

    with review_files[-1].open() as handle:
        payload = json.load(handle)

    rows = []
    for review in payload["reviews"]:
        title_norm = norm(review.get("title", ""))
        if title_norm not in feature_map:
            continue
        base = feature_map[title_norm]
        evaluator = review.get("evaluator", "")
        for category in review.get("evaluations", {}).get("evaluation", {}).get("criteria_scores", []):
            for sub in category.get("subcriteria", []):
                score = parse_float(sub.get("score"))
                if score is None:
                    continue
                row = {
                    "title": base["title"],
                    "title_norm": title_norm,
                    "evaluator": evaluator,
                    "criterion": slugify(sub.get("criterion", "")),
                    "score": score,
                    "target": 1 if score >= 4.0 else 0,
                }
                row.update(base)
                rows.append(row)
    return rows


def median(values):
    ordered = sorted(v for v in values if v is not None)
    if not ordered:
        return 0.0
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def mean(values):
    return sum(values) / len(values) if values else 0.0


def stdev(values):
    if not values:
        return 1.0
    mu = mean(values)
    var = sum((v - mu) ** 2 for v in values) / len(values)
    sd = math.sqrt(var)
    return sd if sd > 1e-12 else 1.0


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def solve_linear_system(matrix, vector):
    n = len(vector)
    a = [row[:] + [vector[i]] for i, row in enumerate(matrix)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("Singular matrix in Newton step")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]

        pivot_val = a[col][col]
        for j in range(col, n + 1):
            a[col][j] /= pivot_val

        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if abs(factor) < 1e-12:
                continue
            for j in range(col, n + 1):
                a[row][j] -= factor * a[col][j]

    return [a[i][n] for i in range(n)]


def sigmoid(value):
    if value >= 0:
        exp_term = math.exp(-value)
        return 1.0 / (1.0 + exp_term)
    exp_term = math.exp(value)
    return exp_term / (1.0 + exp_term)


def balanced_sample_weights(y_vals):
    n_total = len(y_vals)
    n_pos = sum(y_vals)
    n_neg = n_total - n_pos
    if n_pos == 0 or n_neg == 0:
        return [1.0] * n_total
    pos_weight = n_total / (2.0 * n_pos)
    neg_weight = n_total / (2.0 * n_neg)
    return [pos_weight if y_val == 1 else neg_weight for y_val in y_vals]


def fit_logistic_regression(x_rows, y_vals, l2=1.0, max_iter=100, tol=1e-6):
    p = len(x_rows[0])
    beta = [0.0] * p
    sample_weights = balanced_sample_weights(y_vals)

    for _ in range(max_iter):
        probs = [sigmoid(dot(beta, row)) for row in x_rows]
        grad = [0.0] * p
        hess = [[0.0] * p for _ in range(p)]

        for row, y_val, prob, sample_weight in zip(x_rows, y_vals, probs, sample_weights):
            weight = sample_weight * max(prob * (1.0 - prob), 1e-6)
            err = prob - y_val
            for j in range(p):
                grad[j] += sample_weight * row[j] * err
                row_j = row[j]
                for k in range(j, p):
                    hess[j][k] += weight * row_j * row[k]

        for j in range(p):
            if j > 0:
                grad[j] += l2 * beta[j]
                hess[j][j] += l2
            for k in range(j):
                hess[j][k] = hess[k][j]

        step = solve_linear_system(hess, grad)
        beta = [b - s for b, s in zip(beta, step)]
        if max(abs(val) for val in step) < tol:
            break

    return beta


def prepare_design(rows, feature_names, medians=None, means=None, stds=None, fit=False):
    if fit:
        medians = {
            feat: median([row.get(feat) for row in rows if row.get(feat) is not None])
            for feat in feature_names
        }

    filled = []
    for row in rows:
        values = []
        for feat in feature_names:
            value = row.get(feat)
            if value is None:
                value = medians[feat]
            values.append(value)
        filled.append(values)

    if fit:
        means = {
            feat: mean([vals[idx] for vals in filled])
            for idx, feat in enumerate(feature_names)
        }
        stds = {
            feat: stdev([vals[idx] for vals in filled])
            for idx, feat in enumerate(feature_names)
        }

    x_rows = []
    for values in filled:
        x_row = [1.0]
        for idx, feat in enumerate(feature_names):
            x_row.append((values[idx] - means[feat]) / stds[feat])
        x_rows.append(x_row)
    return x_rows, medians, means, stds


def predict_probs(beta, x_rows):
    return [sigmoid(dot(beta, row)) for row in x_rows]


def auc_score(y_true, y_score):
    positives = sum(y_true)
    negatives = len(y_true) - positives
    if positives == 0 or negatives == 0:
        return None

    pairs = sorted(zip(y_score, y_true))
    rank_sum = 0.0
    idx = 0
    rank = 1
    while idx < len(pairs):
        end = idx
        while end < len(pairs) and pairs[end][0] == pairs[idx][0]:
            end += 1
        avg_rank = (rank + (rank + (end - idx) - 1)) / 2.0
        rank_sum += avg_rank * sum(label for _, label in pairs[idx:end])
        rank += end - idx
        idx = end

    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def balanced_accuracy(y_true, y_prob, threshold=0.5):
    positives = sum(y_true)
    negatives = len(y_true) - positives
    if positives == 0 or negatives == 0:
        return None

    preds = [1 if prob >= threshold else 0 for prob in y_prob]
    tp = sum(1 for truth, pred in zip(y_true, preds) if truth == 1 and pred == 1)
    tn = sum(1 for truth, pred in zip(y_true, preds) if truth == 0 and pred == 0)
    tpr = tp / positives if positives else 0.0
    tnr = tn / negatives if negatives else 0.0
    return 0.5 * (tpr + tnr)


def build_group_folds(rows, n_splits=5, seed=42):
    groups = {}
    for row in rows:
        groups.setdefault(row["title_norm"], []).append(row)

    buckets = {0: [], 1: [], 2: [], 3: []}
    for title_norm, group_rows in groups.items():
        pos_count = sum(row["target"] for row in group_rows)
        buckets[pos_count].append(title_norm)

    rng = random.Random(seed)
    folds = [[] for _ in range(n_splits)]
    for bucket_key in sorted(buckets.keys(), reverse=True):
        titles = buckets[bucket_key][:]
        rng.shuffle(titles)
        for idx, title_norm in enumerate(titles):
            folds[idx % n_splits].append(title_norm)
    return folds


def run_cv(rows, feature_names, n_splits=5):
    folds = build_group_folds(rows, n_splits=n_splits)
    fold_metrics = []
    oof_pairs = []

    for test_titles in folds:
        test_title_set = set(test_titles)
        train_rows = [row for row in rows if row["title_norm"] not in test_title_set]
        test_rows = [row for row in rows if row["title_norm"] in test_title_set]

        y_train = [row["target"] for row in train_rows]
        y_test = [row["target"] for row in test_rows]

        x_train, medians, means, stds = prepare_design(train_rows, feature_names, fit=True)
        x_test, _, _, _ = prepare_design(
            test_rows,
            feature_names,
            medians=medians,
            means=means,
            stds=stds,
            fit=False,
        )

        beta = fit_logistic_regression(x_train, y_train, l2=1.0)
        probs = predict_probs(beta, x_test)
        oof_pairs.extend(zip(y_test, probs))
        auc = auc_score(y_test, probs)
        bal_acc = balanced_accuracy(y_test, probs)
        fold_metrics.append(
            {
                "auc": auc,
                "balanced_accuracy": bal_acc,
                "n_test": len(test_rows),
                "positive_rate": mean(y_test),
            }
        )

    auc_vals = [fold["auc"] for fold in fold_metrics if fold["auc"] is not None]
    bal_vals = [
        fold["balanced_accuracy"]
        for fold in fold_metrics
        if fold["balanced_accuracy"] is not None
    ]
    return {
        "folds": fold_metrics,
        "cv_auc_mean": mean(auc_vals),
        "cv_auc_sd": stdev(auc_vals) if len(auc_vals) > 1 else 0.0,
        "cv_bal_acc_mean": mean(bal_vals),
        "cv_bal_acc_sd": stdev(bal_vals) if len(bal_vals) > 1 else 0.0,
        "oof_auc": auc_score([pair[0] for pair in oof_pairs], [pair[1] for pair in oof_pairs]),
        "oof_bal_acc": balanced_accuracy(
            [pair[0] for pair in oof_pairs],
            [pair[1] for pair in oof_pairs],
        ),
    }


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def wrap_label(text, width=20):
    words = str(text).replace("_", " ").split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def interp_color(value, vmin, vmax):
    if vmax <= vmin:
        ratio = 0.5
    else:
        ratio = (value - vmin) / (vmax - vmin)
    ratio = max(0.0, min(1.0, ratio))
    red = int(240 + ratio * (41 - 240))
    green = int(245 + ratio * (128 - 245))
    blue = int(250 + ratio * (185 - 250))
    return f"rgb({red},{green},{blue})"


def render_metrics_svg(metrics_rows, path):
    criteria = [row["criterion"] for row in metrics_rows]
    metrics = [
        ("oof_auc", "OOF AUROC"),
        ("oof_bal_acc", "OOF Balanced Acc."),
        ("positive_rate", "Positive Rate"),
    ]

    cell_w = 150
    cell_h = 52
    left_pad = 280
    top_pad = 90
    width = left_pad + cell_w * len(metrics) + 40
    height = top_pad + cell_h * len(criteria) + 40

    values = []
    for row in metrics_rows:
        for key, _ in metrics:
            values.append(float(row[key]))
    vmin, vmax = min(values), max(values)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="20" y="36" font-size="24" font-family="Helvetica, Arial, sans-serif" font-weight="700">Binary Logistic Regression Performance</text>',
        '<text x="20" y="62" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#444">Rows are criteria; columns summarize grouped 5-fold CV over evaluator-level binary scores.</text>',
    ]

    for col_idx, (_, label) in enumerate(metrics):
        x = left_pad + col_idx * cell_w + cell_w / 2
        parts.append(
            f'<text x="{x}" y="{top_pad - 18}" text-anchor="middle" font-size="14" font-family="Helvetica, Arial, sans-serif" font-weight="600">{label}</text>'
        )

    for row_idx, row in enumerate(metrics_rows):
        y = top_pad + row_idx * cell_h
        label_lines = wrap_label(row["criterion"], width=26)
        label_y = y + cell_h / 2 - (len(label_lines) - 1) * 9
        for offset, line in enumerate(label_lines):
            parts.append(
                f'<text x="20" y="{label_y + offset * 18:.1f}" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#111">{line.title()}</text>'
            )

        for col_idx, (key, _) in enumerate(metrics):
            x = left_pad + col_idx * cell_w
            value = float(row[key])
            fill = interp_color(value, vmin, vmax)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - 8}" height="{cell_h - 8}" rx="8" fill="{fill}" stroke="#d0d7de"/>'
            )
            parts.append(
                f'<text x="{x + (cell_w - 8) / 2}" y="{y + 29}" text-anchor="middle" font-size="18" font-family="Helvetica, Arial, sans-serif" font-weight="700" fill="#111">{value:.3f}</text>'
            )

    parts.append("</svg>")
    path.write_text("\n".join(parts))


def render_bar_svg(rows, value_key, label_key, title, subtitle, path, positive_color, negative_color=None):
    top_n = rows[:12]
    width = 1000
    height = 64 + 44 * len(top_n) + 50
    left_pad = 340
    right_pad = 50
    chart_w = width - left_pad - right_pad

    values = [float(row[value_key]) for row in top_n]
    if negative_color is None:
        min_val = 0.0
        max_val = max(values) if values else 1.0
        origin = left_pad
    else:
        min_val = min(values) if values else -1.0
        max_val = max(values) if values else 1.0
        span = max(abs(min_val), abs(max_val))
        min_val, max_val = -span, span
        origin = left_pad + chart_w * (-min_val) / (max_val - min_val)

    def x_pos(value):
        if max_val <= min_val:
            return left_pad
        return left_pad + chart_w * (value - min_val) / (max_val - min_val)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="20" y="34" font-size="24" font-family="Helvetica, Arial, sans-serif" font-weight="700">{title}</text>',
        f'<text x="20" y="58" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#444">{subtitle}</text>',
    ]

    if negative_color is not None:
        parts.append(
            f'<line x1="{origin:.1f}" y1="72" x2="{origin:.1f}" y2="{height - 24}" stroke="#444" stroke-dasharray="4 4"/>'
        )

    for idx, row in enumerate(top_n):
        y = 88 + idx * 44
        label = str(row[label_key]).replace("_", " ")
        value = float(row[value_key])
        if negative_color is None:
            x0 = origin
            x1 = x_pos(value)
            fill = positive_color
        else:
            x0 = min(origin, x_pos(value))
            x1 = max(origin, x_pos(value))
            fill = positive_color if value >= 0 else negative_color

        parts.append(
            f'<text x="20" y="{y + 18}" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#111">{label}</text>'
        )
        parts.append(
            f'<rect x="{x0:.1f}" y="{y}" width="{max(2.0, x1 - x0):.1f}" height="24" rx="4" fill="{fill}"/>'
        )
        text_anchor = "start" if value >= 0 or negative_color is None else "end"
        text_x = x1 + 8 if value >= 0 or negative_color is None else x0 - 8
        parts.append(
            f'<text x="{text_x:.1f}" y="{y + 17}" text-anchor="{text_anchor}" font-size="13" font-family="Helvetica, Arial, sans-serif" fill="#111">{value:.3f}</text>'
        )

    parts.append("</svg>")
    path.write_text("\n".join(parts))


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    feature_map, feature_names = merge_feature_rows()
    review_rows = load_review_rows(feature_map)
    criteria = sorted({row["criterion"] for row in review_rows})

    metrics_rows = []
    coef_rows = []

    for criterion in criteria:
        criterion_rows = [row for row in review_rows if row["criterion"] == criterion]
        y_vals = [row["target"] for row in criterion_rows]
        cv_metrics = run_cv(criterion_rows, feature_names)
        x_full, medians, means, stds = prepare_design(criterion_rows, feature_names, fit=True)
        beta = fit_logistic_regression(x_full, y_vals, l2=1.0)
        probs = predict_probs(beta, x_full)

        metrics_rows.append(
            {
                "criterion": criterion,
                "n_reviews": len(criterion_rows),
                "n_proposals": len({row["title_norm"] for row in criterion_rows}),
                "positive_rate": mean(y_vals),
                "cv_auc_mean": cv_metrics["cv_auc_mean"],
                "cv_auc_sd": cv_metrics["cv_auc_sd"],
                "cv_bal_acc_mean": cv_metrics["cv_bal_acc_mean"],
                "cv_bal_acc_sd": cv_metrics["cv_bal_acc_sd"],
                "oof_auc": cv_metrics["oof_auc"],
                "oof_bal_acc": cv_metrics["oof_bal_acc"],
                "full_auc": auc_score(y_vals, probs),
            }
        )

        for feat, coef in zip(feature_names, beta[1:]):
            coef_rows.append(
                {
                    "criterion": criterion,
                    "feature": feat,
                    "coef": coef,
                    "abs_coef": abs(coef),
                    "odds_ratio_per_sd": math.exp(coef),
                    "mean": means[feat],
                    "std": stds[feat],
                    "median_impute": medians[feat],
                }
            )

    metrics_rows.sort(key=lambda row: row["criterion"])
    coef_rows.sort(key=lambda row: (row["criterion"], -row["abs_coef"], row["feature"]))

    write_csv(
        TABLES_DIR / "binary_review_logistic_results.csv",
        [
            "criterion",
            "n_reviews",
            "n_proposals",
            "positive_rate",
            "cv_auc_mean",
            "cv_auc_sd",
            "cv_bal_acc_mean",
            "cv_bal_acc_sd",
            "oof_auc",
            "oof_bal_acc",
            "full_auc",
        ],
        metrics_rows,
    )
    write_csv(
        TABLES_DIR / "binary_review_logistic_coefficients.csv",
        [
            "criterion",
            "feature",
            "coef",
            "abs_coef",
            "odds_ratio_per_sd",
            "mean",
            "std",
            "median_impute",
        ],
        coef_rows,
    )

    importance = {}
    for row in coef_rows:
        entry = importance.setdefault(
            row["feature"],
            {"feature": row["feature"], "mean_abs_coef": 0.0, "mean_coef": 0.0, "count": 0},
        )
        entry["mean_abs_coef"] += row["abs_coef"]
        entry["mean_coef"] += row["coef"]
        entry["count"] += 1

    importance_rows = []
    for row in importance.values():
        count = row["count"]
        importance_rows.append(
            {
                "feature": row["feature"],
                "mean_abs_coef": row["mean_abs_coef"] / count,
                "mean_coef": row["mean_coef"] / count,
                "criteria_count": count,
            }
        )

    importance_rows.sort(key=lambda row: (-row["mean_abs_coef"], row["feature"]))
    write_csv(
        TABLES_DIR / "binary_review_logistic_feature_importance.csv",
        ["feature", "mean_abs_coef", "mean_coef", "criteria_count"],
        importance_rows,
    )

    novelty_rows = [
        row
        for row in coef_rows
        if row["criterion"] == "novelty_and_significance"
    ]
    novelty_rows.sort(key=lambda row: row["abs_coef"], reverse=True)

    render_metrics_svg(metrics_rows, FIGURES_DIR / "binary_review_logistic_metrics.svg")
    render_bar_svg(
        importance_rows,
        "mean_abs_coef",
        "feature",
        "Most Predictive Features Across Criteria",
        "Bars show mean absolute standardized coefficients from the full-data logistic models.",
        FIGURES_DIR / "binary_review_logistic_feature_importance.svg",
        positive_color="#1f77b4",
    )
    render_bar_svg(
        novelty_rows,
        "coef",
        "feature",
        "Novelty And Significance Logistic Coefficients",
        "Signed standardized coefficients from the full-data model. Positive means more likely to receive a score >= 4.",
        FIGURES_DIR / "binary_review_logistic_novelty_coefficients.svg",
        positive_color="#2ca02c",
        negative_color="#d62728",
    )

    print("Saved:")
    print(TABLES_DIR / "binary_review_logistic_results.csv")
    print(TABLES_DIR / "binary_review_logistic_coefficients.csv")
    print(TABLES_DIR / "binary_review_logistic_feature_importance.csv")
    print(FIGURES_DIR / "binary_review_logistic_metrics.svg")
    print(FIGURES_DIR / "binary_review_logistic_feature_importance.svg")
    print(FIGURES_DIR / "binary_review_logistic_novelty_coefficients.svg")

    print("\nTop overall features:")
    for row in importance_rows[:10]:
        print(
            f"  {row['feature']:<28} mean|coef|={row['mean_abs_coef']:.3f}  mean coef={row['mean_coef']:+.3f}"
        )

    print("\nCriterion performance:")
    for row in metrics_rows:
        print(
            f"  {row['criterion']:<34} AUROC={row['cv_auc_mean']:.3f}±{row['cv_auc_sd']:.3f}  "
            f"BalAcc={row['oof_bal_acc']:.3f}  OOF AUROC={row['oof_auc']:.3f}  PosRate={row['positive_rate']:.3f}"
        )


if __name__ == "__main__":
    main()

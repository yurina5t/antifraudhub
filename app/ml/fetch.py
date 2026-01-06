# app/ml/fetch.py
import pandas as pd
from typing import Optional


def run_query(query: str, client) -> pd.DataFrame:
    result = client.query(query)
    return pd.DataFrame(result.result_rows, columns=result.column_names)


def _build_features_query(active_days: int, feature_days: int, user_email: Optional[str] = None) -> str:
    """
    Универсальный SQL для агрегации пользовательских фичей.

    - Batch: active_days=7 (кто активен), feature_days=365/730 (агрегация по истории)
    - Single-user: user_email задан, active_days игнорируется логически, feature_days=365/730
    """

    if user_email:
        safe_email = user_email.replace("'", "''")
        # Realtime / single-user режим
        active_users_cte = f"""
        active_users AS (
            SELECT lower(trim('{safe_email}')) AS user_email
        ),
        """
    else:
        # Batch режим
        active_users_cte = f"""
        active_users AS (
            SELECT DISTINCT lower(trim(user_email)) AS user_email
            FROM dbt_mart.dim_merchant_transactions
            WHERE event_date >= today() - {active_days}
              AND transaction_type = 'SALE'
              AND is_test = 0
              AND project != 'adxad'
              AND user_email != ''
        ),
        """

    query = f"""
    WITH
	{active_users_cte}

    dm_features AS (
        SELECT
            lower(trim(user_email)) AS user_email,
            countIf(transaction_type = 'SALE') AS n_sales,
            countIf(transaction_type = 'SALE' AND transaction_status = 'DECLINED') AS n_declines,
            if(n_sales > 0, n_declines / n_sales, 0) AS decline_ratio,
            avgIf(amount, transaction_type = 'SALE') AS avg_sale_amount,
            maxIf(amount, transaction_type = 'SALE') AS max_sale_amount,
            minIf(amount, transaction_type = 'SALE') AS min_sale_amount,
            uniqIf(event_date, transaction_type = 'SALE') AS n_active_days,
            if(n_sales > 0, n_active_days / n_sales, 0) AS sales_density,
            minIf(event_date, transaction_type = 'SALE') AS min_sale_date,
            uniq(source_country) AS unique_countries,
            uniq(card_brand) AS unique_card_brands,
            uniq(gateway) AS unique_gateways,
            uniq(mid) AS unique_mids,
            uniq(site_name) AS unique_sites,
            uniq(project) AS unique_projects,
            countIf(transaction_sub_type = 'trial') AS n_trials,
            countIf(transaction_sub_type = 'rebill') AS n_rebills,
            countIf(transaction_sub_type = 'upgrade') AS n_upgrades,
            countIf(transaction_sub_type = 'conversion') AS n_conversions,
            countIf(transaction_sub_type = 'onetime') AS n_onetime,
            uniq(site_name) > 3 AS multi_site_flag,
            uniq(project) > 2 AS multi_project_flag,
            countIf(bin_country != source_country) > 0 AS geo_mismatch_any,
            anyHeavy(attraction_affiliate_username) AS main_affiliate,
            uniq(attraction_affiliate_username) AS unique_affiliates
        FROM dbt_mart.dim_merchant_transactions
        WHERE 1=1
            AND transaction_type = 'SALE'
            AND is_test = 0
            AND project != 'adxad'
            AND user_email != ''
            AND event_date >= today() - {feature_days}
            AND lower(trim(user_email)) IN (SELECT user_email FROM active_users)
        GROUP BY user_email
    ),
    dc_features AS (
        SELECT
            lower(trim(member_email)) AS user_email,
            uniq(member_id) AS n_members,
            count(*) AS n_dc_events,
            min(attraction_date) AS first_reg_date,
            max(attraction_date) AS last_reg_date,
            uniq(attraction_date) AS n_reg_dates,
            uniq(member_id) / uniq(attraction_date) AS members_per_regdate, 
            anyHeavy(device_type) AS device_type,
            anyHeavy(os) AS os,
            anyHeavy(channel) AS channel,
            avg(is_cross) AS cross_ratio
        FROM dbt_mart.dim_client_paysites_member_transactions
        WHERE 1=1
        AND trans_type IN ('initial','onetime','rebill','trial','conversion')
        AND member_email != ''
        AND attraction_date >= today() - {feature_days}
        AND lower(trim(member_email)) IN (SELECT user_email FROM active_users)
        GROUP BY user_email
    )
    SELECT
        coalesce(dm.user_email, dc.user_email) AS user_email,
        dm.* EXCEPT user_email,
        dc.* EXCEPT user_email
    FROM dm_features dm
    LEFT JOIN dc_features dc
        ON dm.user_email = dc.user_email
    """
    return query


def fetch_user_features_batch(client, active_days: int = 7, feature_days: int = 365) -> pd.DataFrame:
    """
    Batch-агрегация фичей по всем активным пользователям за период.
    """
    query = _build_features_query(
        active_days=active_days,
        feature_days=feature_days,
        user_email=None,
    )
    return run_query(query, client)


def fetch_user_features_user(client, user_email: str, feature_days: int = 365) -> pd.DataFrame:
    """
    Агрегация фичей по одному пользователю за длинный период.
    """
    query = _build_features_query(
        active_days=7,              # любое число так как не важно для user_email режима
        feature_days=feature_days,
        user_email=user_email,
    )
    return run_query(query, client)







# ---------------- чуть позже реализую  ----------------
def fetch_decline_text(client) -> pd.DataFrame:
    """
    Decline-тексты по активным пользователям за 7 дней
    """
    query = f"""
    WITH active_users AS (
        SELECT DISTINCT lower(trim(user_email)) AS user_email
        FROM dbt_mart.dim_merchant_transactions
        WHERE event_date >= today() - 7
            AND transaction_type = 'SALE'
            AND is_test = 0
            AND project != 'adxad'
            AND user_email != ''
        )
    SELECT
        lower(trim(user_email)) AS user_email,
        arrayStringConcat(
            groupArray(DISTINCT lower(trim(response_description))),
            ' '
        ) AS text
    FROM dbt_mart.dim_merchant_transactions
    WHERE transaction_type = 'SALE'
      AND transaction_status = 'DECLINED'
      AND lower(trim(user_email)) IN (SELECT user_email FROM active_users)
    GROUP BY user_email
    """
    return run_query(query, client)


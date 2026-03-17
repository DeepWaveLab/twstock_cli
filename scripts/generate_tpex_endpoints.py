#!/usr/bin/env python3
"""Generate EndpointDef entries for all TPEX OpenAPI endpoints.

Uses a hardcoded endpoint list extracted from the TPEX swagger spec
(https://www.tpex.org.tw/openapi/swagger.json) because the server
drops connections on large downloads.

Usage:
    python scripts/generate_tpex_endpoints.py > /tmp/tpex_endpoints.py
"""

from __future__ import annotations

import sys

# Complete list of TPEX endpoints from swagger.json (path, tag, description)
# Extracted via WebFetch on 2026-03-17
TPEX_ENDPOINTS = [
    # ── 上櫃 (Mainboard OTC) ──
    ("/tpex_mainborad_highlight", "上櫃", "上櫃股票市場現況"),
    ("/tpex_securities", "上櫃", "上櫃股票現股當沖交易標的資訊"),
    ("/tpex_spendi_today", "上櫃", "上櫃當日公布暫停/恢復交易股票"),
    ("/tpex_spendi_history", "上櫃", "上櫃歷史公布暫停/恢復交易股票"),
    ("/tpex_mainboard_daily_close_quotes", "上櫃", "上櫃個股日成交資訊"),
    ("/tpex_mainboard_quotes", "上櫃", "上櫃股票收盤行情"),
    ("/tpex_mainboard_peratio_analysis", "上櫃", "上櫃個股日本益比、殖利率及股價淨值比"),
    ("/tpex_mainboard_margin_balance", "上櫃", "上櫃融資融券餘額"),
    ("/tpex_intraday_trading_statistics", "上櫃", "上櫃當日沖銷交易統計資訊"),
    ("/tpex_active_broker_volume", "上櫃", "上櫃成交量值排行-券商進出排行"),
    ("/tpex_margin_sbl", "上櫃", "上櫃融資融券暨借券餘額"),
    ("/tpex_exright_daily", "上櫃", "上櫃除權除息每日結果"),
    ("/tpex_exright_prepost", "上櫃", "上櫃除權除息預告表"),
    ("/tpex_cmode", "上櫃", "上櫃變更交易方式、股票分割"),
    ("/tpex_odd_stock", "上櫃", "上櫃零股交易行情"),
    ("/tpex_off_market", "上櫃", "上櫃盤後定價交易"),
    ("/tpex_esb_applicant_companies", "上櫃", "上櫃申請登錄興櫃公司"),
    ("/tpex_trading_warning_information", "上櫃", "上櫃公布注意交易資訊"),
    ("/tpex_disposal_information", "上櫃", "上櫃公布處置資訊"),
    ("/tpex_trading_warning_note", "上櫃", "上櫃注意交易資訊累計資料"),
    ("/tpex_margin_trading_term", "上櫃", "上櫃信用交易停止公告"),
    ("/tpex_margin_trading_adjust", "上櫃", "上櫃信用交易調整公告"),
    ("/tpex_margin_trading_lend", "上櫃", "上櫃信用交易融券賣出利率"),
    ("/tpex_margin_trading_marginspot", "上櫃", "上櫃信用交易融資融券餘額"),
    ("/tpex_margin_trading_margin_mark", "上櫃", "上櫃信用交易融資融券標的"),
    ("/tpex_margin_trading_margin_used", "上櫃", "上櫃信用交易融資使用率"),
    ("/tpex_margin_trading_short_sell", "上櫃", "上櫃信用交易借券賣出排行"),
    ("/tpex_3insti_qfii", "上櫃", "上櫃外資及陸資持股排名"),
    ("/tpex_3insti_qfii_industry", "上櫃", "上櫃外資及陸資持股比率按產業別統計表"),
    ("/tpex_3insti_daily_trading", "上櫃", "上櫃三大法人買賣超日報"),
    ("/tpex_3insti_dealer_trading", "上櫃", "上櫃自營商買賣超彙總表"),
    ("/tpex_ceil_non_trading", "上櫃", "上櫃漲跌停未成交買賣資訊"),
    ("/tpex_daily_trading_index", "上櫃", "上櫃每日市場成交資訊"),
    ("/tpex_short_sell", "上櫃", "上櫃借券賣出成交值及餘額"),
    ("/tpex_daily_broker1", "上櫃", "上櫃每日券商營收統計"),
    ("/tpex_active_dollar_volume", "上櫃", "上櫃個股成交金額排行"),
    ("/tpex_active_advanced", "上櫃", "上櫃個股漲幅排行"),
    ("/tpex_active_declined", "上櫃", "上櫃個股跌幅排行"),
    ("/tpex_intraday_fee", "上櫃", "上櫃當沖借券費率"),
    ("/tpex_intraday_trading_pre", "上櫃", "上櫃當沖交易預告停止公告"),
    ("/tpex_intraday_trading_his", "上櫃", "上櫃當沖交易歷史資料"),
    ("/tpex_daily_market_value", "上櫃", "上櫃歷史市值排行"),
    ("/tpex_daily_turnover", "上櫃", "上櫃歷史週轉率排行"),
    ("/tpex_trading_volumes_avg", "上櫃", "上櫃歷史平均成交量"),
    ("/tpex_trading_amount_avg", "上櫃", "上櫃歷史平均成交金額"),
    ("/tpex_trading_volume_ratio", "上櫃", "上櫃歷史成交量值比重"),
    ("/tpex_pe_ratio_top10", "上櫃", "上櫃歷史本益比排行"),
    ("/tpex_daily_qutoes_block", "上櫃", "上櫃鉅額交易每日行情"),
    ("/tpex_daily_trading_block", "上櫃", "上櫃個股鉅額交易每日行情"),
    ("/tpex_daily_trading_summary_odd", "上櫃", "上櫃鉅額交易每日彙總"),
    ("/tpex_monthly_trading_summary_block", "上櫃", "上櫃鉅額交易每月彙總"),
    ("/tpex_yearly_trading_summary_block", "上櫃", "上櫃鉅額交易每年彙總"),
    ("/tpex_volume_rank", "上櫃", "上櫃歷史成交量排行"),
    ("/tpex_amount_rank", "上櫃", "上櫃歷史成交金額排行"),
    ("/tpex_prvol", "上櫃", "上櫃等價成交系統交易分佈"),
    ("/tpex_3insti_summary", "上櫃", "上櫃三大法人買賣金額統計表"),
    ("/tpex_3insti_trading", "上櫃", "上櫃投信買賣超彙總表"),
    ("/tpex_daily_trade_block_day", "上櫃", "上櫃鉅額交易歷史資料"),
    ("/tpex_delayed_stock_open", "上櫃", "上櫃每日延後開盤股票"),
    ("/tpex_delayed_stock_close", "上櫃", "上櫃每日延後收盤股票"),
    ("/tpex_ipo_no_limit", "上櫃", "上櫃IPO五日無漲跌幅資訊"),
    ("/tpex_3insti_qfii_trading", "上櫃", "上櫃外資及陸資買賣超彙總表"),
    # ── 指數系列 (Index Series) ──
    ("/tpex_index", "指數系列", "櫃買指數歷史資料"),
    ("/tpex50_index", "指數系列", "富櫃50指數歷史收盤"),
    ("/tpex200_change", "指數系列", "富櫃200指數每日收盤"),
    ("/tpcgi_constituents", "指數系列", "公司治理指數成份股"),
    ("/tpcgi_reward_index", "指數系列", "公司治理指數歷史收盤"),
    ("/tpcgi_change", "指數系列", "公司治理指數每日收盤"),
    ("/tpex_index_consti", "指數系列", "指數成份股"),
    ("/tpex_reward_index", "指數系列", "指數及報酬指數收盤"),
    ("/tpex50_constituents", "指數系列", "富櫃50成份股"),
    ("/tpex50_change", "指數系列", "富櫃50每日收盤"),
    ("/tphd_constituents", "指數系列", "高股息指數成份股"),
    ("/tphd_change", "指數系列", "高股息指數每日收盤"),
    ("/tpci_constituents", "指數系列", "薪資指數成份股"),
    ("/tpci_change", "指數系列", "薪資指數每日收盤"),
    ("/tpci_reward_index", "指數系列", "薪資指數歷史收盤"),
    ("/tpex_emp88_constituents", "指數系列", "勞就88指數成份股"),
    ("/tpex_emp88_change", "指數系列", "勞就88指數每日收盤"),
    ("/tpex_emp88_reward_index", "指數系列", "勞就88指數歷史收盤"),
    ("/tpex200_constituents", "指數系列", "富櫃200成份股"),
    # ── 債券 (Bonds) ──
    ("/tpex_dpsp_monthly_CBmcs007", "債券", "可轉換公司債ASO/ASW銀行承銷"),
    ("/tpex_international_bond_quotes", "債券", "國際債券盤中行情"),
    ("/tpex_international_bond_trade", "債券", "國際債券盤中成交"),
    ("/tpex_international_bond_issue_investor", "債券", "國際債券一般投資人適用"),
    ("/tpex_international_bond_issue_org", "債券", "國際債券專業投資人適用"),
    ("/BDdos216UTF", "債券", "美金計價固定利率非可贖回債券定價"),
    ("/BDdos215UTF", "債券", "美金計價附息可贖回債券定價"),
    ("/BDdos209UTF", "債券", "美金計價零息可贖回債券定價"),
    # ── 興櫃 (Emerging Stock Board) ──
    ("/tpex_esb_disposal_information", "興櫃", "興櫃處置資訊"),
    ("/tpex_esb_warning_information", "興櫃", "興櫃注意交易資訊"),
    ("/tpex_esb_recommended_dealer", "興櫃", "興櫃推薦證券商及股票"),
    ("/tpex_esb_latest_statistics", "興櫃", "興櫃股票行情"),
    ("/tpex_esb_eps_rank", "興櫃", "興櫃公司EPS排名"),
    ("/tpex_esb_capitals_rank", "興櫃", "興櫃公司實收資本額排名"),
    # ── 創櫃 (GISA) ──
    ("/tpex_gisa_highlight", "創櫃", "創櫃市場概況"),
    ("/tpex_gisa_company", "創櫃", "創櫃公司資訊"),
    ("/tpex_gisa_financing_before", "創櫃", "創櫃登錄前募資"),
    ("/tpex_gisa_financing_history", "創櫃", "創櫃募資系統紀錄"),
    ("/tpex_gisa_financing_in_process", "創櫃", "創櫃處理中募資資訊"),
    # ── 權證 (Warrants) ──
    ("/tpex_warrant_gold", "權證", "黃金現貨權證發行資訊"),
    ("/tpex_warrant_gold_quts", "權證", "黃金現貨權證收盤行情"),
    ("/tpex_warrant_daily_quts", "權證", "權證每日收盤行情"),
    ("/tpex_warrant_monthly_quts", "權證", "權證每月收盤行情"),
    ("/tpex_warrant_issue", "權證", "權證發行資訊"),
    ("/tpex_warrant_wcb_daily_quts", "權證", "牛熊證每日收盤行情"),
    ("/tpex_warrant_wcb_monthly_quts", "權證", "牛熊證每月收盤行情"),
    ("/tpex_warrant_wcb_issue", "權證", "牛熊證發行資訊"),
    ("/tpex_warrant_wxy_daily_quts", "權證", "展延型牛熊證每日收盤行情"),
    ("/tpex_warrant_wxy_monthly_quts", "權證", "展延型牛熊證每月收盤行情"),
    ("/tpex_warrant_wxy_issue", "權證", "展延型牛熊證發行資訊"),
    ("/tpex_warrant_quts", "權證", "個別權證成交資訊"),
    ("/tpex_warrant_statistics", "權證", "權證每日交易參與人統計"),
    ("/tpex_warrant", "權證", "股票權證資訊"),
    ("/tpex_warrant_suspend_today", "權證", "權證當日暫停/恢復交易"),
    ("/tpex_warrant_suspend_history", "權證", "權證歷史暫停/恢復交易"),
    # ── 開放式基金 (Open-ended Funds) ──
    ("/tpex_opfund_latest", "開放式基金", "開放式基金每日行情"),
    ("/tpex_opfund_recommended_dealer", "開放式基金", "開放式基金推薦證券商及基金"),
    ("/tpex_opfund_market_highlight", "開放式基金", "開放式基金市場概況"),
    # ── 黃金現貨 (Gold Spot) ──
    ("/tpex_gold_market_highlight", "黃金現貨", "黃金現貨市場概況"),
    ("/tpex_gold_recommended_dealer", "黃金現貨", "黃金現貨交易商及產品"),
    ("/tpex_gold_latest", "黃金現貨", "黃金現貨每日行情"),
    # ── 公司治理 (Corporate Governance) ──
    ("/t187ap46_O_21", "公司治理", "ESG：職業安全衛生"),
    ("/t187ap46_O_9", "公司治理", "ESG：功能性委員會"),
    ("/t187ap46_O_8", "公司治理", "ESG：氣候治理"),
    ("/t187ap46_O_20", "公司治理", "ESG：反競爭法訴訟"),
    ("/t187ap46_O_19", "公司治理", "ESG：風險管理政策"),
    ("/t187ap46_O_15", "公司治理", "ESG：社區關係"),
    ("/t187ap46_O_13", "公司治理", "ESG：供應鏈管理"),
    ("/t187ap46_O_12", "公司治理", "ESG：食品安全"),
    ("/t187ap46_O_14", "公司治理", "ESG：產品品質安全"),
    ("/t187ap41_O", "公司治理", "股東常會日期地點"),
    ("/t187ap05_R", "公司治理", "興櫃公司每月營業收入"),
    ("/t187ap46_O_4", "公司治理", "ESG：廢棄物管理"),
    ("/t187ap46_O_2", "公司治理", "ESG：能源管理"),
    ("/t187ap46_O_7", "公司治理", "ESG：投資人溝通"),
    ("/t187ap46_O_1", "公司治理", "ESG：溫室氣體排放"),
    ("/t187ap46_O_6", "公司治理", "ESG：董事會"),
    ("/t187ap46_O_5", "公司治理", "ESG：人力資源發展"),
    ("/t187ap46_O_3", "公司治理", "ESG：水資源管理"),
    ("/mopsfin_t187ap05_OA", "公司治理", "29類股營收變動"),
    ("/mopsfin_t187ap05_OB", "公司治理", "發行公司營收重點"),
    ("/t187ap35_O", "公司治理", "股東提案使用情形"),
    ("/mopsfin_t187ap37_O", "公司治理", "認購(售)權證發行彙總"),
    ("/mopsfin_t187ap42_O", "公司治理", "認購(售)權證每日交易"),
    ("/mopsfin_t187ap32_O", "公司治理", "公司治理相關規章"),
    ("/mopsfin_t187ap34_O", "公司治理", "累積投票、委託書徵求方式"),
    ("/mopsfin_t187ap33_O", "公司治理", "董事長兼任總經理"),
    ("/mopsfin_t187ap31_O", "公司治理", "財務報告會計師認可"),
    ("/mopsfin_t187ap09_O", "公司治理", "董監事學經歷"),
    ("/mopsfin_t187ap10_O", "公司治理", "董監事持股不足"),
    ("/mopsfin_t187ap24_O", "公司治理", "營業範圍變更"),
    ("/mopsfin_t187ap25_O", "公司治理", "重大營業變更"),
    ("/mopsfin_t187ap03_O", "公司治理", "上櫃公司基本資料"),
    ("/mopsfin_t187ap36_O", "公司治理", "認購(售)權證年度發行"),
    ("/mopsfin_t187ap03_R", "公司治理", "興櫃公司基本資料"),
    ("/mopsfin_t187ap04_O", "公司治理", "每日重大訊息公告"),
    ("/mopsfin_t187ap01", "公司治理", "券商從業人員按部門統計"),
    ("/mopsfin_t187ap02_O", "公司治理", "持股超過10%大股東"),
    ("/mopsfin_t187ap26_O", "公司治理", "營業範圍變更/下櫃"),
    ("/mopsfin_t187ap27_O", "公司治理", "營業變更為買賣業"),
    ("/mopsfin_t187ap05_O", "公司治理", "上櫃公司每月營業收入彙總表"),
    ("/mopsfin_t187ap39_O", "公司治理", "上櫃公司股利分派情形"),
    # ── 財務報表 (Financial Statements) ──
    ("/mopsfin_t187ap07_O_basi", "財務報表", "資產負債表(金融業)"),
    ("/mopsfin_t187ap07_O_bd", "財務報表", "資產負債表(證券業)"),
    ("/mopsfin_t187ap07_O_ci", "財務報表", "資產負債表(一般業)"),
    ("/mopsfin_t187ap07_O_fh", "財務報表", "資產負債表(金控業)"),
    ("/mopsfin_t187ap07_O_ins", "財務報表", "資產負債表(保險業)"),
    ("/mopsfin_t187ap07_O_mim", "財務報表", "資產負債表(綜合業)"),
    ("/mopsfin_t187ap06_O_basi", "財務報表", "綜合損益表(金融業)"),
    ("/mopsfin_t187ap06_O_bd", "財務報表", "綜合損益表(證券業)"),
    ("/mopsfin_t187ap06_O_ci", "財務報表", "綜合損益表(一般業)"),
    ("/mopsfin_t187ap06_O_fh", "財務報表", "綜合損益表(金控業)"),
    ("/mopsfin_t187ap06_O_ins", "財務報表", "綜合損益表(保險業)"),
    ("/mopsfin_t187ap06_O_mim", "財務報表", "綜合損益表(綜合業)"),
    ("/mopsfin_t187ap06_O_basiA", "財務報表", "財務資訊(金融業)"),
    ("/mopsfin_t187ap06_O_bdA", "財務報表", "財務資訊(證券業)"),
    ("/mopsfin_t187ap06_O_ciA", "財務報表", "財務資訊(一般業)"),
    ("/mopsfin_t187ap06_O_fhA", "財務報表", "財務資訊(金控業)"),
    ("/mopsfin_t187ap06_O_insA", "財務報表", "財務資訊(保險業)"),
    ("/mopsfin_t187ap06_O_mimA", "財務報表", "財務資訊(綜合業)"),
    ("/mopsfin_t187ap07_U_bd", "財務報表", "資產負債表(興櫃-證券業)"),
    ("/mopsfin_t187ap07_U_ci", "財務報表", "資產負債表(興櫃-一般業)"),
    ("/mopsfin_t187ap07_U_fh", "財務報表", "資產負債表(興櫃-金控業)"),
    ("/mopsfin_t187ap07_U_ins", "財務報表", "資產負債表(興櫃-保險業)"),
    ("/mopsfin_t187ap07_U_mim", "財務報表", "資產負債表(興櫃-綜合業)"),
    ("/mopsfin_t187ap06_U_basi", "財務報表", "綜合損益表(興櫃-金融業)"),
    ("/mopsfin_t187ap06_U_bd", "財務報表", "綜合損益表(興櫃-證券業)"),
    ("/mopsfin_t187ap06_U_ci", "財務報表", "綜合損益表(興櫃-一般業)"),
    ("/mopsfin_t187ap06_U_fh", "財務報表", "綜合損益表(興櫃-金控業)"),
    ("/mopsfin_t187ap06_U_ins", "財務報表", "綜合損益表(興櫃-保險業)"),
    ("/mopsfin_t187ap06_U_mim", "財務報表", "綜合損益表(興櫃-綜合業)"),
    ("/mopsfin_t187ap07_U_basi", "財務報表", "資產負債表(興櫃-金融業)"),
    ("/mopsfin_t187ap11_R", "財務報表", "興櫃董監事持股餘額明細"),
    ("/mopsfin_t187ap14_O", "財務報表", "上櫃各產業EPS統計"),
    ("/mopsfin_t187ap15_O", "財務報表", "季累計營收預估"),
    ("/mopsfin_t187ap16_O", "財務報表", "季營收偏離統計"),
    ("/mopsfin_187ap17_O", "財務報表", "獲利分析查詢彙總"),
    # ── 券商資料 (Broker Data) ──
    ("/mopsfin_t187ap08_O", "券商資料", "董監事持股不足明細"),
    ("/mopsfin_t187ap11_O", "券商資料", "上櫃公司董監事持股餘額明細資料"),
    ("/mopsfin_t187ap12_O", "券商資料", "內部人股票轉讓申報"),
    ("/mopsfin_t187ap13_O", "券商資料", "內部人未轉讓持股"),
    ("/mopsfin_t187ap22_O", "券商資料", "金管會證券訴訟案件"),
    ("/mopsfin_t187ap30_O", "券商資料", "獨立董事兼職"),
    ("/mopsfin_t187ap29_A_O", "券商資料", "董事酬金資訊"),
    ("/mopsfin_t187ap29_B_O", "券商資料", "監察人酬金資訊"),
    ("/bond_cb_daily", "券商資料", "可轉債每日券商進出"),
]

# Phase 1 endpoints already in endpoints.py (by API path)
EXISTING_PATHS = {
    "/tpex_mainboard_daily_close_quotes",
    "/tpex_mainboard_quotes",
    "/tpex_3insti_daily_trading",
    "/tpex_3insti_summary",
    "/tpex_3insti_qfii_trading",
    "/tpex_3insti_qfii",
    "/tpex_3insti_qfii_industry",
    "/tpex_mainboard_margin_balance",
    "/tpex_mainboard_peratio_analysis",
    "/tpex_exright_prepost",
    "/tpex_exright_daily",
    "/tpex_index",
    "/tpex_intraday_trading_statistics",
    "/tpex_odd_stock",
    "/tpex_off_market",
    "/tpex_mainborad_highlight",
    "/tpex_daily_trading_index",
    "/tpex_esb_latest_statistics",
    "/mopsfin_t187ap03_O",
    "/mopsfin_t187ap05_O",
    "/mopsfin_t187ap06_O_ci",
    "/mopsfin_t187ap07_O_ci",
    "/mopsfin_t187ap11_O",
    "/mopsfin_t187ap14_O",
    "/mopsfin_t187ap39_O",
}

# Tag → group mapping
TAG_TO_GROUP = {
    "上櫃": "otc",
    "指數系列": "otc_index",
    "公司治理": "otc_company",
    "財務報表": "otc_financial",
    "興櫃": "otc_esb",
    "創櫃": "otc_gisa",
    "權證": "otc_warrant",
    "開放式基金": "otc_fund",
    "黃金現貨": "otc_gold",
    "債券": "otc_bond",
    "券商資料": "otc_broker",
}


def determine_group(path: str, tag: str) -> str:
    """Determine endpoint group from tag and path."""
    name = path.lstrip("/")
    # ESG endpoints → separate group
    if name.startswith("t187ap46_"):
        return "otc_esg"
    # t187ap* non-ESG under 公司治理 → otc_company
    if tag == "公司治理" and name.startswith("t187ap"):
        return "otc_company"
    return TAG_TO_GROUP.get(tag, "otc")


def path_to_cli_name(path: str, group: str) -> str:
    """Convert API path to CLI-friendly name."""
    name = path.lstrip("/")
    # Strip known prefixes by group
    prefixes = {
        "otc": "tpex_",
        "otc_index": "",
        "otc_company": "mopsfin_",
        "otc_esg": "",
        "otc_financial": "mopsfin_",
        "otc_esb": "tpex_esb_",
        "otc_gisa": "tpex_gisa_",
        "otc_warrant": "tpex_",
        "otc_fund": "tpex_opfund_",
        "otc_gold": "tpex_gold_",
        "otc_bond": "",
        "otc_broker": "mopsfin_",
    }
    prefix = prefixes.get(group, "")
    if prefix and name.startswith(prefix):
        name = name[len(prefix):]
    return name.replace("_", "-").lower()


def main():
    new_endpoints = []
    for path, tag, desc in TPEX_ENDPOINTS:
        if path in EXISTING_PATHS:
            continue
        group = determine_group(path, tag)
        cli_name = path_to_cli_name(path, group)
        new_endpoints.append((path, group, cli_name, desc))

    print(f"Total TPEX endpoints in spec: {len(TPEX_ENDPOINTS)}", file=sys.stderr)
    print(f"Already registered (Phase 1): {len(EXISTING_PATHS)}", file=sys.stderr)
    print(f"New endpoints to add: {len(new_endpoints)}", file=sys.stderr)

    # Group by category
    by_group: dict[str, list[tuple]] = {}
    for ep in new_endpoints:
        by_group.setdefault(ep[1], []).append(ep)

    group_labels = {
        "otc": "TPEX (OTC) stock trading — Phase 2",
        "otc_index": "TPEX (OTC) index series",
        "otc_company": "TPEX (OTC) company/governance",
        "otc_esg": "TPEX (OTC) ESG disclosures",
        "otc_financial": "TPEX (OTC) financial statements",
        "otc_esb": "TPEX (OTC) emerging stock board",
        "otc_gisa": "TPEX (OTC) GISA (創櫃)",
        "otc_warrant": "TPEX (OTC) warrants",
        "otc_fund": "TPEX (OTC) open-ended funds",
        "otc_gold": "TPEX (OTC) gold spot",
        "otc_bond": "TPEX (OTC) bonds",
        "otc_broker": "TPEX (OTC) broker/insider data",
    }

    group_order = [
        "otc", "otc_index", "otc_company", "otc_esg", "otc_financial",
        "otc_esb", "otc_gisa", "otc_warrant", "otc_fund", "otc_gold",
        "otc_bond", "otc_broker",
    ]

    for group in group_order:
        eps = by_group.get(group, [])
        if not eps:
            continue
        label = group_labels.get(group, group)
        dashes = "─" * max(1, 56 - len(label))
        print(f"    # ── {label} {dashes}──")
        for path, grp, cli_name, desc in eps:
            key = f"{grp}.{cli_name}"
            print(f'    "{key}": EndpointDef(')
            print(f'        path="{path}",')
            print(f'        cli_name="{cli_name}",')
            print(f'        group="{grp}",')
            print(f'        description="{desc}",')
            print(f"        base_url=TPEX_BASE_URL,")
            print(f"    ),")

    print(f"\nSummary by group:", file=sys.stderr)
    for group in group_order:
        eps = by_group.get(group, [])
        if eps:
            print(f"  {group}: {len(eps)}", file=sys.stderr)
    print(f"  TOTAL NEW: {len(new_endpoints)}", file=sys.stderr)


if __name__ == "__main__":
    main()

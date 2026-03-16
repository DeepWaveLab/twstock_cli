"""Endpoint registry — 143 TWSE OpenAPI endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EndpointDef:
    """Definition of a single TWSE OpenAPI endpoint."""

    path: str
    cli_name: str
    group: str
    description: str
    code_field: str | None = None
    fields: list[str] = field(default_factory=list)


ENDPOINTS: dict[str, EndpointDef] = {
    "company.punish": EndpointDef(
        path="/announcement/punish",
        cli_name="punish",
        group="company",
        description="集中市場公布處置股票",
    ),
    "company.applylistingforeign": EndpointDef(
        path="/company/applylistingForeign",
        cli_name="applylistingforeign",
        group="company",
        description="外國公司向證交所申請第一上市之公司",
    ),
    "company.applylistinglocal": EndpointDef(
        path="/company/applylistingLocal",
        cli_name="applylistinglocal",
        group="company",
        description="申請上市之本國公司",
    ),
    "company.newlisting": EndpointDef(
        path="/company/newlisting",
        cli_name="newlisting",
        group="company",
        description="最近上市公司",
    ),
    "company.suspendlistingcsvandhtml": EndpointDef(
        path="/company/suspendListingCsvAndHtml",
        cli_name="suspendlistingcsvandhtml",
        group="company",
        description="終止上市公司",
    ),
    "company.t187ap02-l": EndpointDef(
        path="/opendata/t187ap02_L",
        cli_name="t187ap02-l",
        group="company",
        description="上市公司持股逾 10% 大股東名單",
        code_field="公司代號",
    ),
    "company.t187ap03-l": EndpointDef(
        path="/opendata/t187ap03_L",
        cli_name="t187ap03-l",
        group="company",
        description="上市公司基本資料",
        code_field="公司代號",
        fields=["出表日期", "公司代號", "公司名稱", "公司簡稱", "產業別", "住址", "董事長", "總經理", "成立日期", "上市日期", "實收資本額"],
    ),
    "company.t187ap03-p": EndpointDef(
        path="/opendata/t187ap03_P",
        cli_name="t187ap03-p",
        group="company",
        description="公開發行公司基本資料",
        code_field="公司代號",
    ),
    "company.t187ap04-l": EndpointDef(
        path="/opendata/t187ap04_L",
        cli_name="t187ap04-l",
        group="company",
        description="上市公司每日重大訊息",
        code_field="公司代號",
    ),
    "company.t187ap05-p": EndpointDef(
        path="/opendata/t187ap05_P",
        cli_name="t187ap05-p",
        group="company",
        description="公開發行公司每月營業收入彙總表",
        code_field="公司代號",
    ),
    "company.t187ap08-l": EndpointDef(
        path="/opendata/t187ap08_L",
        cli_name="t187ap08-l",
        group="company",
        description="上市公司董事、監察人持股不足法定成數彙總表",
        code_field="公司代號",
    ),
    "company.t187ap09-l": EndpointDef(
        path="/opendata/t187ap09_L",
        cli_name="t187ap09-l",
        group="company",
        description="上市公司董事、監察人質權設定占董事及監察人實際持有股數彙總表",
        code_field="公司代號",
    ),
    "company.t187ap10-l": EndpointDef(
        path="/opendata/t187ap10_L",
        cli_name="t187ap10-l",
        group="company",
        description="上市公司董事、監察人持股不足法定成數連續達3個月以上彙總表",
        code_field="公司代號",
    ),
    "company.t187ap11-l": EndpointDef(
        path="/opendata/t187ap11_L",
        cli_name="t187ap11-l",
        group="company",
        description="上市公司董監事持股餘額明細資料",
        code_field="公司代號",
    ),
    "company.t187ap12-l": EndpointDef(
        path="/opendata/t187ap12_L",
        cli_name="t187ap12-l",
        group="company",
        description="上市公司每日內部人持股轉讓事前申報表-持股轉讓日報表",
        code_field="公司代號",
    ),
    "company.t187ap13-l": EndpointDef(
        path="/opendata/t187ap13_L",
        cli_name="t187ap13-l",
        group="company",
        description="上市公司每日內部人持股轉讓事前申報表-持股未轉讓日報表",
        code_field="公司代號",
    ),
    "company.t187ap14-l": EndpointDef(
        path="/opendata/t187ap14_L",
        cli_name="t187ap14-l",
        group="company",
        description="上市公司各產業EPS統計資訊",
        code_field="公司代號",
    ),
    "company.t187ap22-l": EndpointDef(
        path="/opendata/t187ap22_L",
        cli_name="t187ap22-l",
        group="company",
        description="上市公司金管會證券期貨局裁罰案件專區",
        code_field="公司代號",
    ),
    "company.t187ap23-l": EndpointDef(
        path="/opendata/t187ap23_L",
        cli_name="t187ap23-l",
        group="company",
        description="上市公司違反資訊申報、重大訊息及說明記者會規定專區",
        code_field="公司代號",
    ),
    "company.t187ap24-l": EndpointDef(
        path="/opendata/t187ap24_L",
        cli_name="t187ap24-l",
        group="company",
        description="上市公司經營權及營業範圍異(變)動專區-經營權異動公司",
        code_field="公司代號",
    ),
    "company.t187ap25-l": EndpointDef(
        path="/opendata/t187ap25_L",
        cli_name="t187ap25-l",
        group="company",
        description="上市公司經營權及營業範圍異(變)動專區-營業範圍重大變更公司",
        code_field="公司代號",
    ),
    "company.t187ap26-l": EndpointDef(
        path="/opendata/t187ap26_L",
        cli_name="t187ap26-l",
        group="company",
        description="上市公司經營權及營業範圍異(變)動專區-經營權異動且營業範圍重大變更停止買賣公司",
        code_field="公司代號",
    ),
    "company.t187ap27-l": EndpointDef(
        path="/opendata/t187ap27_L",
        cli_name="t187ap27-l",
        group="company",
        description="上市公司經營權及營業範圍異(變)動專區-經營權異動且營業範圍重大變更列為變更交易公司",
        code_field="公司代號",
    ),
    "company.t187ap29-a-l": EndpointDef(
        path="/opendata/t187ap29_A_L",
        cli_name="t187ap29-a-l",
        group="company",
        description="上市公司董事酬金相關資訊 ",
        code_field="公司代號",
    ),
    "company.t187ap29-b-l": EndpointDef(
        path="/opendata/t187ap29_B_L",
        cli_name="t187ap29-b-l",
        group="company",
        description="上市公司監察人酬金相關資訊 ",
        code_field="公司代號",
    ),
    "company.t187ap29-c-l": EndpointDef(
        path="/opendata/t187ap29_C_L",
        cli_name="t187ap29-c-l",
        group="company",
        description="上市公司合併報表董事酬金相關資訊 ",
        code_field="公司代號",
    ),
    "company.t187ap29-d-l": EndpointDef(
        path="/opendata/t187ap29_D_L",
        cli_name="t187ap29-d-l",
        group="company",
        description="上市公司合併報表監察人酬金相關資訊 ",
        code_field="公司代號",
    ),
    "company.t187ap30-l": EndpointDef(
        path="/opendata/t187ap30_L",
        cli_name="t187ap30-l",
        group="company",
        description="上市公司獨立董監事兼任情形彙總表",
        code_field="公司代號",
    ),
    "company.t187ap32-l": EndpointDef(
        path="/opendata/t187ap32_L",
        cli_name="t187ap32-l",
        group="company",
        description="上市公司公司治理之相關規程規則",
        code_field="公司代號",
    ),
    "company.t187ap33-l": EndpointDef(
        path="/opendata/t187ap33_L",
        cli_name="t187ap33-l",
        group="company",
        description="上市公司董事長是否兼任總經理",
        code_field="公司代號",
    ),
    "company.t187ap34-l": EndpointDef(
        path="/opendata/t187ap34_L",
        cli_name="t187ap34-l",
        group="company",
        description="上市公司採累積投票制、全額連記法、候選人提名制選任董監事及當選資料彙總表",
        code_field="公司代號",
    ),
    "company.t187ap35-l": EndpointDef(
        path="/opendata/t187ap35_L",
        cli_name="t187ap35-l",
        group="company",
        description="上市公司股東行使提案權情形彙總表",
        code_field="公司代號",
    ),
    "company.t187ap38-l": EndpointDef(
        path="/opendata/t187ap38_L",
        cli_name="t187ap38-l",
        group="company",
        description="上市公司股東會公告-召集股東常(臨時)會公告資料彙總表(95年度起適用)",
        code_field="公司代號",
    ),
    "company.t187ap41-l": EndpointDef(
        path="/opendata/t187ap41_L",
        cli_name="t187ap41-l",
        group="company",
        description="上市公司召開股東常 (臨時) 會日期、地點及採用電子投票情形等資料彙總表",
        code_field="公司代號",
    ),
    "company.t187ap45-l": EndpointDef(
        path="/opendata/t187ap45_L",
        cli_name="t187ap45-l",
        group="company",
        description="上市公司股利分派情形",
        code_field="公司代號",
        fields=["出表日期", "公司代號", "公司名稱", "股利年度", "股東配發-盈餘分配之現金股利(元/股)", "股東配發-盈餘轉增資配股(元/股)"],
    ),
    "company.t187ap46-l-1": EndpointDef(
        path="/opendata/t187ap46_L_1",
        cli_name="t187ap46-l-1",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-溫室氣體排放",
        code_field="公司代號",
    ),
    "company.t187ap46-l-10": EndpointDef(
        path="/opendata/t187ap46_L_10",
        cli_name="t187ap46-l-10",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-燃料管理",
        code_field="公司代號",
    ),
    "company.t187ap46-l-11": EndpointDef(
        path="/opendata/t187ap46_L_11",
        cli_name="t187ap46-l-11",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-產品生命週期",
        code_field="公司代號",
    ),
    "company.t187ap46-l-12": EndpointDef(
        path="/opendata/t187ap46_L_12",
        cli_name="t187ap46-l-12",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-食品安全",
        code_field="公司代號",
    ),
    "company.t187ap46-l-13": EndpointDef(
        path="/opendata/t187ap46_L_13",
        cli_name="t187ap46-l-13",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-供應鏈管理",
        code_field="公司代號",
    ),
    "company.t187ap46-l-14": EndpointDef(
        path="/opendata/t187ap46_L_14",
        cli_name="t187ap46-l-14",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-產品品質與安全",
        code_field="公司代號",
    ),
    "company.t187ap46-l-15": EndpointDef(
        path="/opendata/t187ap46_L_15",
        cli_name="t187ap46-l-15",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-社區關係",
        code_field="公司代號",
    ),
    "company.t187ap46-l-16": EndpointDef(
        path="/opendata/t187ap46_L_16",
        cli_name="t187ap46-l-16",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-資訊安全",
        code_field="公司代號",
    ),
    "company.t187ap46-l-17": EndpointDef(
        path="/opendata/t187ap46_L_17",
        cli_name="t187ap46-l-17",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-普惠金融",
        code_field="公司代號",
    ),
    "company.t187ap46-l-18": EndpointDef(
        path="/opendata/t187ap46_L_18",
        cli_name="t187ap46-l-18",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-持股及控制力",
        code_field="公司代號",
    ),
    "company.t187ap46-l-19": EndpointDef(
        path="/opendata/t187ap46_L_19",
        cli_name="t187ap46-l-19",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-風險管理政策",
        code_field="公司代號",
    ),
    "company.t187ap46-l-2": EndpointDef(
        path="/opendata/t187ap46_L_2",
        cli_name="t187ap46-l-2",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-能源管理",
        code_field="公司代號",
    ),
    "company.t187ap46-l-20": EndpointDef(
        path="/opendata/t187ap46_L_20",
        cli_name="t187ap46-l-20",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-反競爭行為法律訴訟",
        code_field="公司代號",
    ),
    "company.t187ap46-l-21": EndpointDef(
        path="/opendata/t187ap46_L_21",
        cli_name="t187ap46-l-21",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-職業安全衛生",
        code_field="公司代號",
    ),
    "company.t187ap46-l-3": EndpointDef(
        path="/opendata/t187ap46_L_3",
        cli_name="t187ap46-l-3",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-水資源管理",
        code_field="公司代號",
    ),
    "company.t187ap46-l-4": EndpointDef(
        path="/opendata/t187ap46_L_4",
        cli_name="t187ap46-l-4",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-廢棄物管理",
        code_field="公司代號",
    ),
    "company.t187ap46-l-5": EndpointDef(
        path="/opendata/t187ap46_L_5",
        cli_name="t187ap46-l-5",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-人力發展",
        code_field="公司代號",
    ),
    "company.t187ap46-l-6": EndpointDef(
        path="/opendata/t187ap46_L_6",
        cli_name="t187ap46-l-6",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-董事會",
        code_field="公司代號",
    ),
    "company.t187ap46-l-7": EndpointDef(
        path="/opendata/t187ap46_L_7",
        cli_name="t187ap46-l-7",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-投資人溝通",
        code_field="公司代號",
    ),
    "company.t187ap46-l-8": EndpointDef(
        path="/opendata/t187ap46_L_8",
        cli_name="t187ap46-l-8",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-氣候相關議題管理",
        code_field="公司代號",
    ),
    "company.t187ap46-l-9": EndpointDef(
        path="/opendata/t187ap46_L_9",
        cli_name="t187ap46-l-9",
        group="company",
        description="上市公司企業ESG資訊揭露彙總資料-功能性委員會",
        code_field="公司代號",
    ),
    "other.bfi61u": EndpointDef(
        path="/exchangeReport/BFI61U",
        cli_name="bfi61u",
        group="other",
        description="中央登錄公債補息資料表",
        code_field="Code",
    ),
    "other.eventlist": EndpointDef(
        path="/news/eventList",
        cli_name="eventlist",
        group="other",
        description="證交所活動訊息",
    ),
    "other.newslist": EndpointDef(
        path="/news/newsList",
        cli_name="newslist",
        group="other",
        description="證交所新聞",
    ),
    "other.t187ap47-l": EndpointDef(
        path="/opendata/t187ap47_L",
        cli_name="t187ap47-l",
        group="other",
        description="基金基本資料彙總表",
        code_field="公司代號",
    ),
    "broker.etfrank": EndpointDef(
        path="/ETFReport/ETFRank",
        cli_name="etfrank",
        group="broker",
        description="定期定額交易戶數統計排行月報表",
    ),
    "broker.brokerlist": EndpointDef(
        path="/brokerService/brokerList",
        cli_name="brokerlist",
        group="broker",
        description="證券商總公司基本資料",
        code_field="Code",
        fields=["Code", "Name", "EstablishmentDate", "Address", "Telephone"],
    ),
    "broker.secregdata": EndpointDef(
        path="/brokerService/secRegData",
        cli_name="secregdata",
        group="broker",
        description="開辦定期定額業務證券商名單",
        code_field="Code",
    ),
    "broker.opendata-brk01": EndpointDef(
        path="/opendata/OpenData_BRK01",
        cli_name="opendata-brk01",
        group="broker",
        description="證券商營業員男女人數統計資料",
        code_field="公司代號",
    ),
    "broker.opendata-brk02": EndpointDef(
        path="/opendata/OpenData_BRK02",
        cli_name="opendata-brk02",
        group="broker",
        description="證券商分公司基本資料",
        code_field="公司代號",
    ),
    "broker.t187ap01": EndpointDef(
        path="/opendata/t187ap01",
        cli_name="t187ap01",
        group="broker",
        description="券商業務別人員數",
        code_field="公司代號",
    ),
    "broker.t187ap18": EndpointDef(
        path="/opendata/t187ap18",
        cli_name="t187ap18",
        group="broker",
        description="證券商基本資料",
        code_field="公司代號",
    ),
    "broker.t187ap20": EndpointDef(
        path="/opendata/t187ap20",
        cli_name="t187ap20",
        group="broker",
        description="各券商每月月計表",
        code_field="公司代號",
    ),
    "broker.t187ap21": EndpointDef(
        path="/opendata/t187ap21",
        cli_name="t187ap21",
        group="broker",
        description="各券商收支概況表資料",
        code_field="公司代號",
    ),
    "stock.mi-index4": EndpointDef(
        path="/exchangeReport/MI_INDEX4",
        cli_name="mi-index4",
        group="stock",
        description="每日上市上櫃跨市場成交資訊",
        code_field="Code",
    ),
    "stock.frmsa": EndpointDef(
        path="/indicesReport/FRMSA",
        cli_name="frmsa",
        group="stock",
        description="寶島股價指數歷史資料",
    ),
    "stock.mfi94u": EndpointDef(
        path="/indicesReport/MFI94U",
        cli_name="mfi94u",
        group="stock",
        description="發行量加權股價報酬指數",
    ),
    "stock.mi-5mins-hist": EndpointDef(
        path="/indicesReport/MI_5MINS_HIST",
        cli_name="mi-5mins-hist",
        group="stock",
        description="發行量加權股價指數歷史資料",
    ),
    "stock.tai50i": EndpointDef(
        path="/indicesReport/TAI50I",
        cli_name="tai50i",
        group="stock",
        description="臺灣 50 指數歷史資料",
    ),
    "stock.t187ap36-l": EndpointDef(
        path="/opendata/t187ap36_L",
        cli_name="t187ap36-l",
        group="stock",
        description="上市認購(售)權證年度發行量概況統計表",
        code_field="公司代號",
    ),
    "stock.t187ap42-l": EndpointDef(
        path="/opendata/t187ap42_L",
        cli_name="t187ap42-l",
        group="stock",
        description="上市認購(售)權證每日成交資料檔",
        code_field="公司代號",
    ),
    "stock.t187ap43-l": EndpointDef(
        path="/opendata/t187ap43_L",
        cli_name="t187ap43-l",
        group="stock",
        description="上市認購(售)權證交易人數檔",
        code_field="公司代號",
    ),
    "stock.bfzfzu-t": EndpointDef(
        path="/Announcement/BFZFZU_T",
        cli_name="bfzfzu-t",
        group="stock",
        description="投資理財節目異常推介個股",
    ),
    "stock.twt96u": EndpointDef(
        path="/SBL/TWT96U",
        cli_name="twt96u",
        group="stock",
        description="上市上櫃股票當日可借券賣出股數",
    ),
    "stock.notetrans": EndpointDef(
        path="/announcement/notetrans",
        cli_name="notetrans",
        group="stock",
        description="集中市場公布注意累計次數異常資訊",
    ),
    "stock.notice": EndpointDef(
        path="/announcement/notice",
        cli_name="notice",
        group="stock",
        description="集中市場當日公布注意股票",
    ),
    "stock.bfiauu-d": EndpointDef(
        path="/block/BFIAUU_d",
        cli_name="bfiauu-d",
        group="stock",
        description="集中市場鉅額交易日成交量值統計",
    ),
    "stock.bfiauu-m": EndpointDef(
        path="/block/BFIAUU_m",
        cli_name="bfiauu-m",
        group="stock",
        description="集中市場鉅額交易月成交量值統計",
    ),
    "stock.bfiauu-y": EndpointDef(
        path="/block/BFIAUU_y",
        cli_name="bfiauu-y",
        group="stock",
        description="集中市場鉅額交易年成交量值統計",
    ),
    "stock.bfi84u": EndpointDef(
        path="/exchangeReport/BFI84U",
        cli_name="bfi84u",
        group="stock",
        description="集中市場停資停券預告表",
        code_field="Code",
    ),
    "stock.bft41u": EndpointDef(
        path="/exchangeReport/BFT41U",
        cli_name="bft41u",
        group="stock",
        description="集中市場盤後定價交易",
        code_field="Code",
    ),
    "stock.bwibbu-all": EndpointDef(
        path="/exchangeReport/BWIBBU_ALL",
        cli_name="bwibbu-all",
        group="stock",
        description="上市個股日本益比、殖利率及股價淨值比（依代碼查詢）",
        code_field="Code",
        fields=["Code", "Name", "PEratio", "DividendYield", "PBratio"],
    ),
    "stock.bwibbu-d": EndpointDef(
        path="/exchangeReport/BWIBBU_d",
        cli_name="bwibbu-d",
        group="stock",
        description="上市個股日本益比、殖利率及股價淨值比（依日期查詢）",
        code_field="Code",
    ),
    "stock.fmnptk-all": EndpointDef(
        path="/exchangeReport/FMNPTK_ALL",
        cli_name="fmnptk-all",
        group="stock",
        description="上市個股年成交資訊",
        code_field="Code",
    ),
    "stock.fmsrfk-all": EndpointDef(
        path="/exchangeReport/FMSRFK_ALL",
        cli_name="fmsrfk-all",
        group="stock",
        description="上市個股月成交資訊",
        code_field="Code",
    ),
    "stock.fmtqik": EndpointDef(
        path="/exchangeReport/FMTQIK",
        cli_name="fmtqik",
        group="stock",
        description="集中市場每日市場成交資訊",
        code_field="Code",
    ),
    "stock.mi-5mins": EndpointDef(
        path="/exchangeReport/MI_5MINS",
        cli_name="mi-5mins",
        group="stock",
        description="每 5 秒委託成交統計",
        code_field="Code",
    ),
    "stock.mi-index": EndpointDef(
        path="/exchangeReport/MI_INDEX",
        cli_name="mi-index",
        group="stock",
        description="每日收盤行情-大盤統計資訊",
        code_field="Code",
        fields=["日期", "指數", "收盤指數", "漲跌", "漲跌點數", "漲跌百分比", "特殊處理註記"],
    ),
    "stock.mi-index20": EndpointDef(
        path="/exchangeReport/MI_INDEX20",
        cli_name="mi-index20",
        group="stock",
        description="集中市場每日成交量前二十名證券",
        code_field="Code",
    ),
    "stock.mi-margn": EndpointDef(
        path="/exchangeReport/MI_MARGN",
        cli_name="mi-margn",
        group="stock",
        description="集中市場融資融券餘額",
        code_field="Code",
    ),
    "stock.stock-day-all": EndpointDef(
        path="/exchangeReport/STOCK_DAY_ALL",
        cli_name="stock-day-all",
        group="stock",
        description="上市個股日成交資訊",
        code_field="Code",
        fields=["Code", "Name", "TradeVolume", "TradeValue", "OpeningPrice", "HighestPrice", "LowestPrice", "ClosingPrice", "Change", "Transaction"],
    ),
    "stock.stock-day-avg-all": EndpointDef(
        path="/exchangeReport/STOCK_DAY_AVG_ALL",
        cli_name="stock-day-avg-all",
        group="stock",
        description="上市個股日收盤價及月平均價",
        code_field="Code",
        fields=["Code", "Name", "ClosingPrice", "MonthlyAveragePrice"],
    ),
    "stock.stock-first": EndpointDef(
        path="/exchangeReport/STOCK_FIRST",
        cli_name="stock-first",
        group="stock",
        description="每日第一上市外國股票成交量值",
        code_field="Code",
    ),
    "stock.twt48u-all": EndpointDef(
        path="/exchangeReport/TWT48U_ALL",
        cli_name="twt48u-all",
        group="stock",
        description="上市股票除權除息預告表",
        code_field="Code",
    ),
    "stock.twt53u": EndpointDef(
        path="/exchangeReport/TWT53U",
        cli_name="twt53u",
        group="stock",
        description="集中市場零股交易行情單",
        code_field="Code",
    ),
    "stock.twt84u": EndpointDef(
        path="/exchangeReport/TWT84U",
        cli_name="twt84u",
        group="stock",
        description="上市個股股價升降幅度",
        code_field="Code",
    ),
    "stock.twt85u": EndpointDef(
        path="/exchangeReport/TWT85U",
        cli_name="twt85u",
        group="stock",
        description="集中市場證券變更交易",
        code_field="Code",
    ),
    "stock.twt88u": EndpointDef(
        path="/exchangeReport/TWT88U",
        cli_name="twt88u",
        group="stock",
        description="上市個股首五日無漲跌幅",
        code_field="Code",
    ),
    "stock.twtawu": EndpointDef(
        path="/exchangeReport/TWTAWU",
        cli_name="twtawu",
        group="stock",
        description="集中市場暫停交易證券",
        code_field="Code",
    ),
    "stock.twtb4u": EndpointDef(
        path="/exchangeReport/TWTB4U",
        cli_name="twtb4u",
        group="stock",
        description="上市股票每日當日沖銷交易標的及統計",
        code_field="Code",
    ),
    "stock.twtbau1": EndpointDef(
        path="/exchangeReport/TWTBAU1",
        cli_name="twtbau1",
        group="stock",
        description="集中市場暫停先賣後買當日沖銷交易標的預告表",
        code_field="Code",
    ),
    "stock.twtbau2": EndpointDef(
        path="/exchangeReport/TWTBAU2",
        cli_name="twtbau2",
        group="stock",
        description="集中市場暫停先賣後買當日沖銷交易歷史查詢",
        code_field="Code",
    ),
    "stock.mi-qfiis-cat": EndpointDef(
        path="/fund/MI_QFIIS_cat",
        cli_name="mi-qfiis-cat",
        group="stock",
        description="集中市場外資及陸資投資類股持股比率表",
    ),
    "stock.mi-qfiis-sort-20": EndpointDef(
        path="/fund/MI_QFIIS_sort_20",
        cli_name="mi-qfiis-sort-20",
        group="stock",
        description="集中市場外資及陸資持股前 20 名彙總表",
    ),
    "stock.holidayschedule": EndpointDef(
        path="/holidaySchedule/holidaySchedule",
        cli_name="holidayschedule",
        group="stock",
        description="有價證券集中交易市場開（休）市日期",
    ),
    "stock.t187ap19": EndpointDef(
        path="/opendata/t187ap19",
        cli_name="t187ap19",
        group="stock",
        description="電子式交易統計資訊",
        code_field="公司代號",
    ),
    "stock.t187ap37-l": EndpointDef(
        path="/opendata/t187ap37_L",
        cli_name="t187ap37-l",
        group="stock",
        description="上市權證基本資料彙總表",
        code_field="公司代號",
    ),
    "stock.twtazu-od": EndpointDef(
        path="/opendata/twtazu_od",
        cli_name="twtazu-od",
        group="stock",
        description="集中市場漲跌證券數統計表",
        code_field="公司代號",
    ),
    "company.t187ap05-l": EndpointDef(
        path="/opendata/t187ap05_L",
        cli_name="t187ap05-l",
        group="company",
        description="上市公司每月營業收入彙總表",
        code_field="公司代號",
        fields=["出表日期", "資料年月", "公司代號", "公司名稱", "產業別", "營業收入-當月營收", "營業收入-去年當月營收", "營業收入-去年同月增減(%)"],
    ),
    "company.t187ap06-l-basi": EndpointDef(
        path="/opendata/t187ap06_L_basi",
        cli_name="t187ap06-l-basi",
        group="company",
        description="上市公司綜合損益表(金融業)",
        code_field="公司代號",
    ),
    "company.t187ap06-l-bd": EndpointDef(
        path="/opendata/t187ap06_L_bd",
        cli_name="t187ap06-l-bd",
        group="company",
        description="上市公司綜合損益表(證券期貨業)",
        code_field="公司代號",
    ),
    "company.t187ap06-l-ci": EndpointDef(
        path="/opendata/t187ap06_L_ci",
        cli_name="t187ap06-l-ci",
        group="company",
        description="上市公司綜合損益表(一般業)",
        code_field="公司代號",
    ),
    "company.t187ap06-l-fh": EndpointDef(
        path="/opendata/t187ap06_L_fh",
        cli_name="t187ap06-l-fh",
        group="company",
        description="上市公司綜合損益表(金控業)",
        code_field="公司代號",
    ),
    "company.t187ap06-l-ins": EndpointDef(
        path="/opendata/t187ap06_L_ins",
        cli_name="t187ap06-l-ins",
        group="company",
        description="上市公司綜合損益表(保險業)",
        code_field="公司代號",
    ),
    "company.t187ap06-l-mim": EndpointDef(
        path="/opendata/t187ap06_L_mim",
        cli_name="t187ap06-l-mim",
        group="company",
        description="上市公司綜合損益表(異業)",
        code_field="公司代號",
    ),
    "company.t187ap06-x-basi": EndpointDef(
        path="/opendata/t187ap06_X_basi",
        cli_name="t187ap06-x-basi",
        group="company",
        description="公發公司綜合損益表-金融業",
        code_field="公司代號",
    ),
    "company.t187ap06-x-bd": EndpointDef(
        path="/opendata/t187ap06_X_bd",
        cli_name="t187ap06-x-bd",
        group="company",
        description="公發公司綜合損益表-證券期貨業",
        code_field="公司代號",
    ),
    "company.t187ap06-x-ci": EndpointDef(
        path="/opendata/t187ap06_X_ci",
        cli_name="t187ap06-x-ci",
        group="company",
        description="公發公司綜合損益表-一般業",
        code_field="公司代號",
    ),
    "company.t187ap06-x-fh": EndpointDef(
        path="/opendata/t187ap06_X_fh",
        cli_name="t187ap06-x-fh",
        group="company",
        description="公發公司綜合損益表-金控業",
        code_field="公司代號",
    ),
    "company.t187ap06-x-ins": EndpointDef(
        path="/opendata/t187ap06_X_ins",
        cli_name="t187ap06-x-ins",
        group="company",
        description="公發公司綜合損益表-保險業",
        code_field="公司代號",
    ),
    "company.t187ap06-x-mim": EndpointDef(
        path="/opendata/t187ap06_X_mim",
        cli_name="t187ap06-x-mim",
        group="company",
        description="公發公司綜合損益表-異業",
        code_field="公司代號",
    ),
    "company.t187ap07-l-basi": EndpointDef(
        path="/opendata/t187ap07_L_basi",
        cli_name="t187ap07-l-basi",
        group="company",
        description="上市公司資產負債表(金融業)",
        code_field="公司代號",
    ),
    "company.t187ap07-l-bd": EndpointDef(
        path="/opendata/t187ap07_L_bd",
        cli_name="t187ap07-l-bd",
        group="company",
        description="上市公司資產負債表(證券期貨業)",
        code_field="公司代號",
    ),
    "company.t187ap07-l-ci": EndpointDef(
        path="/opendata/t187ap07_L_ci",
        cli_name="t187ap07-l-ci",
        group="company",
        description="上市公司資產負債表(一般業)",
        code_field="公司代號",
    ),
    "company.t187ap07-l-fh": EndpointDef(
        path="/opendata/t187ap07_L_fh",
        cli_name="t187ap07-l-fh",
        group="company",
        description="上市公司資產負債表(金控業)",
        code_field="公司代號",
    ),
    "company.t187ap07-l-ins": EndpointDef(
        path="/opendata/t187ap07_L_ins",
        cli_name="t187ap07-l-ins",
        group="company",
        description="上市公司資產負債表(保險業)",
        code_field="公司代號",
    ),
    "company.t187ap07-l-mim": EndpointDef(
        path="/opendata/t187ap07_L_mim",
        cli_name="t187ap07-l-mim",
        group="company",
        description="上市公司資產負債表(異業)",
        code_field="公司代號",
    ),
    "company.t187ap07-x-basi": EndpointDef(
        path="/opendata/t187ap07_X_basi",
        cli_name="t187ap07-x-basi",
        group="company",
        description="公發公司資產負債表-金融業",
        code_field="公司代號",
    ),
    "company.t187ap07-x-bd": EndpointDef(
        path="/opendata/t187ap07_X_bd",
        cli_name="t187ap07-x-bd",
        group="company",
        description="公發公司資產負債表-證券期貨業",
        code_field="公司代號",
    ),
    "company.t187ap07-x-ci": EndpointDef(
        path="/opendata/t187ap07_X_ci",
        cli_name="t187ap07-x-ci",
        group="company",
        description="公發公司資產負債表-一般業",
        code_field="公司代號",
    ),
    "company.t187ap07-x-fh": EndpointDef(
        path="/opendata/t187ap07_X_fh",
        cli_name="t187ap07-x-fh",
        group="company",
        description="公發公司資產負債表-金控業",
        code_field="公司代號",
    ),
    "company.t187ap07-x-ins": EndpointDef(
        path="/opendata/t187ap07_X_ins",
        cli_name="t187ap07-x-ins",
        group="company",
        description="公發公司資產負債表-保險業",
        code_field="公司代號",
    ),
    "company.t187ap07-x-mim": EndpointDef(
        path="/opendata/t187ap07_X_mim",
        cli_name="t187ap07-x-mim",
        group="company",
        description="公發公司資產負債表-異業",
        code_field="公司代號",
    ),
    "company.t187ap11-p": EndpointDef(
        path="/opendata/t187ap11_P",
        cli_name="t187ap11-p",
        group="company",
        description="公發公司董監事持股餘額明細",
        code_field="公司代號",
    ),
    "company.t187ap15-l": EndpointDef(
        path="/opendata/t187ap15_L",
        cli_name="t187ap15-l",
        group="company",
        description="上市公司截至各季綜合損益財測達成情形(簡式)",
        code_field="公司代號",
    ),
    "company.t187ap16-l": EndpointDef(
        path="/opendata/t187ap16_L",
        cli_name="t187ap16-l",
        group="company",
        description="上市公司當季綜合損益經會計師查核(核閱)數與當季預測數差異達百分之十以上者，或截至當季累計差異達百分之二十以上者(簡式)",
        code_field="公司代號",
    ),
    "company.t187ap17-l": EndpointDef(
        path="/opendata/t187ap17_L",
        cli_name="t187ap17-l",
        group="company",
        description="上市公司營益分析查詢彙總表(全體公司彙總報表)",
        code_field="公司代號",
    ),
    "company.t187ap31-l": EndpointDef(
        path="/opendata/t187ap31_L",
        cli_name="t187ap31-l",
        group="company",
        description="上市公司財務報告經監察人承認情形",
        code_field="公司代號",
    ),
}


def resolve_endpoint(ref: str) -> EndpointDef | None:
    """Resolve dotted name, raw path, or API code to EndpointDef.

    Accepts:
        - Dotted name: "stock.stock-day-all"
        - Raw API path: "/exchangeReport/STOCK_DAY_ALL"
        - API code: "STOCK_DAY_ALL"
    """
    # Direct dotted name match
    if ref in ENDPOINTS:
        return ENDPOINTS[ref]

    # Raw path match
    path = ref if ref.startswith("/") else f"/{ref}"
    for ep in ENDPOINTS.values():
        if ep.path == path:
            return ep

    # API code match (case-insensitive)
    ref_lower = ref.lower().replace("_", "-")
    for key, ep in ENDPOINTS.items():
        if ep.cli_name == ref_lower:
            return ep
        # Also try matching the last segment of the path
        path_code = ep.path.split("/")[-1].lower().replace("_", "-")
        if path_code == ref_lower:
            return ep

    return None


def list_endpoints(*, category: str | None = None, search: str | None = None, with_fields: bool = False) -> list[dict]:
    """List endpoints for discovery.

    Args:
        category: Filter by group (stock, company, broker, other).
        search: Search keyword in name, description, or path.
        with_fields: Include field definitions in output.
    """
    results = []
    search_lower = search.lower() if search else None

    for key, ep in sorted(ENDPOINTS.items()):
        if category and ep.group != category:
            continue

        if search_lower:
            searchable = f"{key} {ep.description} {ep.path}".lower()
            if search_lower not in searchable:
                continue

        entry: dict = {
            "name": key,
            "path": ep.path,
            "group": ep.group,
            "description": ep.description,
        }
        if with_fields and ep.fields:
            entry["fields"] = ep.fields
        results.append(entry)

    return results

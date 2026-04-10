const API_BASE_URL = "https://api.frankfurter.dev/v2";
const DEFAULT_FROM = "USD";
const DEFAULT_TO = "RUB";
const FORECAST_MODE_STORAGE_KEY = "currency-flow-forecast-mode";
const LANGUAGE_STORAGE_KEY = "currency-flow-language";

const amountInput = document.getElementById("amountInput");
const fromCurrencySelect = document.getElementById("fromCurrency");
const toCurrencySelect = document.getElementById("toCurrency");
const swapButton = document.getElementById("swapButton");
const resultValue = document.getElementById("resultValue");
const resultHint = document.getElementById("resultHint");
const rateLine = document.getElementById("rateLine");
const updatedLine = document.getElementById("updatedLine");
const statusBox = document.getElementById("statusBox");
const resultState = document.getElementById("resultState");
const liveBadge = document.getElementById("liveBadge");
const currencyPickers = Array.from(document.querySelectorAll(".currency-picker"));
const chartRangeButtons = Array.from(document.querySelectorAll(".chart-range-button"));
const historyChart = document.getElementById("historyChart");
const chartStateBox = document.getElementById("chartStateBox");
const chartSubtitle = document.getElementById("chartSubtitle");
const chartMin = document.getElementById("chartMin");
const chartMax = document.getElementById("chartMax");
const chartLatest = document.getElementById("chartLatest");
const forecastModeButtons = Array.from(document.querySelectorAll(".forecast-mode-button"));
const copyForecastButton = document.getElementById("copyForecastButton");
const forecastDisclaimer = document.getElementById("forecastDisclaimer");
const forecastSummary = document.getElementById("forecastSummary");
const forecastDeltaLine = document.getElementById("forecastDeltaLine");
const forecastDirection = document.getElementById("forecastDirection");
const forecastSpot = document.getElementById("forecastSpot");
const forecastSpotContext = document.getElementById("forecastSpotContext");
const forecastTomorrowCard = document.getElementById("forecastTomorrowCard");
const forecastTomorrow = document.getElementById("forecastTomorrow");
const forecastTomorrowDelta = document.getElementById("forecastTomorrowDelta");
const forecastTomorrowRange = document.getElementById("forecastTomorrowRange");
const forecastWeekCard = document.getElementById("forecastWeekCard");
const forecastWeek = document.getElementById("forecastWeek");
const forecastWeekDelta = document.getElementById("forecastWeekDelta");
const forecastWeekRange = document.getElementById("forecastWeekRange");
const forecastMonthCard = document.getElementById("forecastMonthCard");
const forecastMonth = document.getElementById("forecastMonth");
const forecastMonthDelta = document.getElementById("forecastMonthDelta");
const forecastMonthRange = document.getElementById("forecastMonthRange");
const forecastConfidence = document.getElementById("forecastConfidence");
const forecastContext = document.getElementById("forecastContext");
const forecastReason = document.getElementById("forecastReason");
const forecastInsight = document.getElementById("forecastInsight");
const forecastSignalStrength = document.getElementById("forecastSignalStrength");
const forecastVolatility = document.getElementById("forecastVolatility");
const forecastMode = document.getElementById("forecastMode");
const languageButtons = Array.from(document.querySelectorAll(".language-switch__button"));

const appState = {
  currencies: [],
  currencyMap: new Map(),
  activeRequestId: 0,
  activeChartRequestId: 0,
  chartRangeDays: 7,
  forecastMode: "conservative",
  locale: "ru",
  historyCache: new Map(),
  pickers: new Map(),
  latestRatePayload: null,
  currentChartPoints: [],
  currentForecastPoints: []
};

const translations = {
  ru: {
    doc: {
      title: "Currency Flow | Онлайн-конвертер валют"
    },
    language: {
      aria: "Переключатель языка"
    },
    hero: {
      title: "Онлайн-конвертер валют с актуальными курсами",
      lead: "Пересчитывайте суммы между мировыми валютами в реальном времени. Курсы загружаются из Frankfurter API и автоматически обновляются при каждом изменении суммы или пары валют.",
      metaAria: "Преимущества",
      pillLive: "Живые данные",
      pillInstant: "Мгновенный пересчёт",
      pillMobile: "Удобно на мобильных устройствах"
    },
    converter: {
      kicker: "Конвертер",
      title: "Перевод суммы по текущему курсу",
      amountLabel: "Сумма",
      amountPlaceholder: "Введите сумму",
      amountFootnote: "Автопересчёт без кнопки подтверждения",
      fromLabel: "Из валюты",
      toLabel: "В валюту",
      fromAria: "Исходная валюта",
      toAria: "Целевая валюта",
      showAllCurrencies: "Показать все валюты",
      searchPlaceholder: "Введите код или название валюты",
      currencyListAria: "Список валют",
      swap: "Обмен",
      swapAria: "Поменять валюты местами",
      chooseCurrency: "Выберите валюту"
    },
    result: {
      label: "Результат",
      pill: "Актуальные данные",
      currentRateLabel: "Текущий курс",
      sourceLabel: "Источник и время"
    },
    chart: {
      kicker: "Динамика курса",
      title: "Историческое движение выбранной валютной пары",
      defaultSubtitle: "Показываем, как менялся курс выбранной пары за последний период.",
      pairSubtitle: "Пара {from} → {to}. Период: {range}.",
      periodAria: "Период графика",
      rangeWeek: "Неделя",
      rangeMonth: "Месяц",
      rangeYear: "Год",
      rangeLabelWeek: "последняя неделя",
      rangeLabelMonth: "последний месяц",
      rangeLabelYear: "последний год",
      rangeLabelDays: "последние {days} дней",
      minLabel: "Минимум",
      maxLabel: "Максимум",
      latestLabel: "Последняя точка",
      aria: "График динамики курса",
      loading: "Загружаем исторические данные…",
      empty: "Недостаточно данных для построения графика.",
      sameCurrency: "Для одинаковых валют исторический график не требуется.",
      loadingPair: "Загружаем историческую динамику по выбранной валютной паре…",
      peak: "Пик",
      low: "Мин",
      now: "Сейчас"
    },
    forecast: {
      kicker: "Предполагаемая оценка",
      title: "Модельная оценка курса",
      metaAria: "Как считается оценка",
      metaHistory: "История для оценки: 365 дней",
      metaFact: "График выше показывает факт",
      metaSeparate: "Оценка считается отдельно",
      spotLabel: "Текущий курс",
      tomorrowLabel: "На завтра",
      weekLabel: "Через 7 дней",
      monthLabel: "Через 30 дней",
      confidenceLabel: "Уверенность модели",
      signalLabel: "Сила сигнала",
      volatilityLabel: "Волатильность",
      modeLabel: "Режим модели",
      modeSwitchAria: "Режим модели",
      modeConservative: "Консервативный",
      modeNeutral: "Нейтральный",
      modeAggressive: "Агрессивный",
      copy: "Скопировать вывод",
      copied: "Скопировано",
      copyFailed: "Не удалось скопировать",
      legend: "Как читать модель: график выше показывает фактическое движение пары, а блок ниже даёт сценарную оценку по годовой истории. Стрелка показывает направление, `Δ к текущему` показывает относительное изменение, диапазон показывает коридор возможного движения при текущей волатильности.",
      disclaimer: "Предполагаемая оценка: ориентир по историческим данным и текущей волатильности, не инвестиционная рекомендация.",
      awaiting: "Ожидание данных",
      summaryDefault: "Оценка строится по длинной истории курса и обновляется при смене пары валют.",
      deltaDefault: "Базовый сценарий на 30 дней: -",
      reasonDefault: "Модель ожидает загрузки данных для объяснения сценария.",
      insightDefault: "Ключевой вывод модели появится после загрузки исторических данных.",
      notEnoughHistory: "Для предполагаемой оценки нужно больше длинной истории по выбранной паре.",
      directionSideways: "Боковой сценарий",
      directionUp: "Осторожный рост",
      directionDown: "Осторожное снижение",
      spotContext: "База расчёта: 1 {base} = {rate} {quote}",
      deltaVsCurrent: "Δ к текущему: {value}",
      range: "Диапазон: {lower} - {upper} {quote}",
      context: "История: 365д · проверка: {sample} точек",
      summaryDynamic: "Для пары {from} → {to} модель использует годовую историю, сглаживает разовые всплески и оценивает ближайший сценарий на нескольких горизонтах.",
      deltaDynamic: "Базовый сценарий на 30 дней: {value}",
      reasonSideways: "Сигнал остаётся слабым: после сглаживания шума и сверки с недавней историей модель не видит уверенного перевеса ни в рост, ни в снижение.",
      reasonUp: "Модель видит согласованный восходящий импульс на нескольких горизонтах, и недавняя проверка не считает его случайным шумом.",
      reasonDown: "Модель видит согласованный нисходящий импульс на нескольких горизонтах, и недавняя проверка не считает его случайным шумом.",
      insightSideways: "Ключевой вывод: для пары {pair} базовый сценарий остаётся близким к боковому движению, поэтому модель не закладывает выраженный тренд.",
      insightUp: "Ключевой вывод: для пары {pair} модель допускает умеренный рост курса на месячном горизонте относительно текущей точки.",
      insightDown: "Ключевой вывод: для пары {pair} модель допускает умеренное снижение курса на месячном горизонте относительно текущей точки.",
      signalLow: "Низкая",
      signalMedium: "Средняя",
      signalHigh: "Повышенная",
      volatilityCalm: "Спокойная",
      volatilityModerate: "Умеренная",
      volatilityHigh: "Высокая",
      biasSideways: "приоритет бокового сценария",
      biasUp: "умеренный восходящий уклон",
      biasDown: "умеренный нисходящий уклон",
      summaryHeading: "## Предполагаемая оценка курса",
      summaryScenario: "**Сценарий:** {value}",
      summarySpot: "**Текущий курс:** {value}",
      summaryTomorrow: "**На завтра:** {value}",
      summaryWeek: "**Через 7 дней:** {value}",
      summaryMonth: "**Через 30 дней:** {value}",
      summaryParamsHeading: "### Параметры модели",
      summaryConfidence: "- Уверенность: {value}",
      summarySignal: "- Сила сигнала: {value}",
      summaryVolatility: "- Волатильность: {value}",
      summaryMode: "- Режим модели: {value}",
      summaryInterpretationHeading: "### Интерпретация"
    },
    status: {
      idleValue: "Введите сумму",
      idleHint: "Конвертация появится сразу после ввода данных.",
      idleUpdated: "Покажем дату и источник после первого успешного запроса.",
      waiting: "Ожидание",
      ready: "Готово к расчёту. Используются актуальные онлайн-данные Frankfurter API.",
      awaitingInput: "Ожидание ввода",
      invalidValue: "Некорректная сумма",
      invalidHint: "Введите положительное число или оставьте поле пустым.",
      invalidUpdated: "Сначала нужно указать корректную сумму для расчёта.",
      invalidState: "Проверьте ввод",
      invalidStatus: "Сумма должна быть числом не меньше нуля.",
      inputErrorBadge: "Ошибка ввода",
      loadingValue: "Загружаем курс",
      loadingHint: "Считаем сумму по актуальным данным и обновляем карточку результата...",
      loadingRate: "Обновляем курс",
      loadingUpdated: "Получаем свежий курс из Frankfurter API",
      loadingState: "Загрузка",
      loadingStatus: "Подключаемся к Frankfurter API и обновляем актуальный курс.",
      loadingBadge: "Загрузка",
      errorValue: "Курс недоступен",
      errorHint: "Мы не смогли обновить актуальные данные. Попробуйте ещё раз через пару секунд.",
      errorState: "Ошибка",
      apiErrorBadge: "Ошибка API",
      successState: "Онлайн",
      successStatus: "Конвертация выполнена по актуальным данным Frankfurter API.",
      successBadge: "Онлайн-курс",
      updatedWithDate: "Источник: Frankfurter API, дата курса {date}. Обновлено в интерфейсе {updatedAt}.",
      updatedWithoutDate: "Источник: Frankfurter API. Обновлено в интерфейсе {updatedAt}.",
      resultHint: "{amount} {from} по текущему курсу в {to}.",
      sameCurrencyHint: "Обе валюты одинаковые, поэтому сумма не меняется.",
      sameCurrencyUpdated: "Локальный пересчёт без API, обновлено {updatedAt}.",
      noRate: "Без курса",
      sameCurrencyStatus: "Одинаковая валютная пара не требует внешнего запроса.",
      sameCurrencyBadge: "Та же валюта",
      currenciesLoaded: "Список валют загружен. Данные будут рассчитываться через Frankfurter API.",
      apiReady: "API готов",
      noConnectionValue: "Нет соединения",
      noConnectionHint: "Не удалось загрузить список валют для конвертера.",
      noConnectionRate: "Курс временно недоступен",
      noConnectionUpdated: "Проверьте соединение и обновите страницу.",
      noApiBadge: "Нет API"
    },
    picker: {
      empty: "Ничего не найдено. Попробуйте другой код или название."
    },
    errors: {
      loadCurrencies: "Не удалось получить список валют.",
      loadHistorical: "Не удалось загрузить исторические данные.",
      loadLatestRate: "Не удалось загрузить актуальный курс.",
      incompleteRate: "Сервис вернул неполные данные по курсу.",
      chartUnavailable: "Не удалось загрузить исторический график.",
      rateUnavailable: "Не удалось получить курс валют.",
      longHistoryUnavailable: "График загружен, но для предполагаемой оценки не удалось получить длинную историю.",
      connectApi: "Не удалось подключиться к Frankfurter API."
    }
  },
  en: {
    doc: {
      title: "Currency Flow | Online Currency Converter"
    },
    language: {
      aria: "Language switcher"
    },
    hero: {
      title: "Online currency converter with live exchange rates",
      lead: "Convert amounts between major world currencies in real time. Rates are loaded from the Frankfurter API and refresh automatically whenever the amount or currency pair changes.",
      metaAria: "Benefits",
      pillLive: "Live data",
      pillInstant: "Instant recalculation",
      pillMobile: "Comfortable on mobile devices"
    },
    converter: {
      kicker: "Converter",
      title: "Convert an amount at the current rate",
      amountLabel: "Amount",
      amountPlaceholder: "Enter amount",
      amountFootnote: "Auto recalculation without a confirm button",
      fromLabel: "From",
      toLabel: "To",
      fromAria: "Source currency",
      toAria: "Target currency",
      showAllCurrencies: "Show all currencies",
      searchPlaceholder: "Type a currency code or name",
      currencyListAria: "Currency list",
      swap: "Swap",
      swapAria: "Swap currencies",
      chooseCurrency: "Choose a currency"
    },
    result: {
      label: "Result",
      pill: "Live data",
      currentRateLabel: "Current rate",
      sourceLabel: "Source and time"
    },
    chart: {
      kicker: "Rate dynamics",
      title: "Historical movement of the selected currency pair",
      defaultSubtitle: "See how the selected pair has moved over the chosen period.",
      pairSubtitle: "Pair {from} → {to}. Period: {range}.",
      periodAria: "Chart period",
      rangeWeek: "Week",
      rangeMonth: "Month",
      rangeYear: "Year",
      rangeLabelWeek: "last week",
      rangeLabelMonth: "last month",
      rangeLabelYear: "last year",
      rangeLabelDays: "last {days} days",
      minLabel: "Minimum",
      maxLabel: "Maximum",
      latestLabel: "Latest point",
      aria: "Exchange-rate history chart",
      loading: "Loading historical data…",
      empty: "Not enough data to build the chart.",
      sameCurrency: "A historical chart is not needed for identical currencies.",
      loadingPair: "Loading historical movement for the selected currency pair…",
      peak: "Peak",
      low: "Low",
      now: "Now"
    },
    forecast: {
      kicker: "Estimated outlook",
      title: "Model-based exchange-rate outlook",
      metaAria: "How the outlook is calculated",
      metaHistory: "History used for outlook: 365 days",
      metaFact: "The chart above shows observed data",
      metaSeparate: "The outlook is calculated separately",
      spotLabel: "Current rate",
      tomorrowLabel: "Tomorrow",
      weekLabel: "In 7 days",
      monthLabel: "In 30 days",
      confidenceLabel: "Model confidence",
      signalLabel: "Signal strength",
      volatilityLabel: "Volatility",
      modeLabel: "Model mode",
      modeSwitchAria: "Model mode",
      modeConservative: "Conservative",
      modeNeutral: "Neutral",
      modeAggressive: "Aggressive",
      copy: "Copy summary",
      copied: "Copied",
      copyFailed: "Copy failed",
      legend: "How to read the model: the chart above shows the actual pair movement, while the block below gives a scenario-based outlook from one year of history. The arrow shows direction, `Δ vs current` shows relative change, and the range shows a possible corridor under current volatility.",
      disclaimer: "Estimated outlook: a guide based on historical data and current volatility, not investment advice.",
      awaiting: "Waiting for data",
      summaryDefault: "The outlook uses a long exchange-rate history and refreshes when the currency pair changes.",
      deltaDefault: "Base 30-day scenario: -",
      reasonDefault: "The model is waiting for data to explain the scenario.",
      insightDefault: "A key model takeaway will appear once historical data is loaded.",
      notEnoughHistory: "The estimated outlook needs a longer history for the selected pair.",
      directionSideways: "Sideways scenario",
      directionUp: "Cautious upside",
      directionDown: "Cautious downside",
      spotContext: "Model base: 1 {base} = {rate} {quote}",
      deltaVsCurrent: "Δ vs current: {value}",
      range: "Range: {lower} - {upper} {quote}",
      context: "History: 365d · validation: {sample} points",
      summaryDynamic: "For {from} → {to}, the model uses one year of history, smooths one-off spikes, and estimates the nearest scenario across several horizons.",
      deltaDynamic: "Base 30-day scenario: {value}",
      reasonSideways: "The signal remains weak: after smoothing noise and checking against recent history, the model does not see a clear edge for either upside or downside.",
      reasonUp: "The model sees a consistent upward impulse across multiple horizons, and recent validation does not treat it as random noise.",
      reasonDown: "The model sees a consistent downward impulse across multiple horizons, and recent validation does not treat it as random noise.",
      insightSideways: "Key takeaway: for {pair}, the base scenario remains close to sideways movement, so the model does not assume a pronounced trend.",
      insightUp: "Key takeaway: for {pair}, the model allows for a moderate increase in the pair rate over the monthly horizon relative to the current point.",
      insightDown: "Key takeaway: for {pair}, the model allows for a moderate decrease in the pair rate over the monthly horizon relative to the current point.",
      signalLow: "Low",
      signalMedium: "Medium",
      signalHigh: "Elevated",
      volatilityCalm: "Calm",
      volatilityModerate: "Moderate",
      volatilityHigh: "High",
      biasSideways: "sideways bias",
      biasUp: "moderate upward bias",
      biasDown: "moderate downward bias",
      summaryHeading: "## Estimated exchange-rate outlook",
      summaryScenario: "**Scenario:** {value}",
      summarySpot: "**Current rate:** {value}",
      summaryTomorrow: "**Tomorrow:** {value}",
      summaryWeek: "**In 7 days:** {value}",
      summaryMonth: "**In 30 days:** {value}",
      summaryParamsHeading: "### Model parameters",
      summaryConfidence: "- Confidence: {value}",
      summarySignal: "- Signal strength: {value}",
      summaryVolatility: "- Volatility: {value}",
      summaryMode: "- Model mode: {value}",
      summaryInterpretationHeading: "### Interpretation"
    },
    status: {
      idleValue: "Enter an amount",
      idleHint: "The conversion will appear as soon as you start typing.",
      idleUpdated: "We will show the source and timestamp after the first successful request.",
      waiting: "Waiting",
      ready: "Ready to convert. Live online data from the Frankfurter API is used.",
      awaitingInput: "Waiting for input",
      invalidValue: "Invalid amount",
      invalidHint: "Enter a positive number or leave the field empty.",
      invalidUpdated: "A valid amount is required before we can calculate.",
      invalidState: "Check the input",
      invalidStatus: "The amount must be a number greater than or equal to zero.",
      inputErrorBadge: "Input error",
      loadingValue: "Loading rate",
      loadingHint: "Calculating the amount with live data and updating the result card…",
      loadingRate: "Updating rate",
      loadingUpdated: "Requesting the latest rate from Frankfurter API",
      loadingState: "Loading",
      loadingStatus: "Connecting to the Frankfurter API and updating the current rate.",
      loadingBadge: "Loading",
      errorValue: "Rate unavailable",
      errorHint: "We could not refresh the live data. Please try again in a few seconds.",
      errorState: "Error",
      apiErrorBadge: "API error",
      successState: "Online",
      successStatus: "Conversion completed using current Frankfurter API data.",
      successBadge: "Online rate",
      updatedWithDate: "Source: Frankfurter API, rate date {date}. Updated in the interface at {updatedAt}.",
      updatedWithoutDate: "Source: Frankfurter API. Updated in the interface at {updatedAt}.",
      resultHint: "{amount} {from} at the current rate in {to}.",
      sameCurrencyHint: "Both currencies are the same, so the amount does not change.",
      sameCurrencyUpdated: "Local calculation without an API call, updated at {updatedAt}.",
      noRate: "No rate",
      sameCurrencyStatus: "An identical currency pair does not require an external request.",
      sameCurrencyBadge: "Same currency",
      currenciesLoaded: "The currency list is loaded. Data will be calculated via the Frankfurter API.",
      apiReady: "API ready",
      noConnectionValue: "No connection",
      noConnectionHint: "Could not load the currency list for the converter.",
      noConnectionRate: "Rate temporarily unavailable",
      noConnectionUpdated: "Check your connection and refresh the page.",
      noApiBadge: "No API"
    },
    picker: {
      empty: "Nothing found. Try another currency code or name."
    },
    errors: {
      loadCurrencies: "Could not load the currency list.",
      loadHistorical: "Could not load historical data.",
      loadLatestRate: "Could not load the latest exchange rate.",
      incompleteRate: "The service returned incomplete exchange-rate data.",
      chartUnavailable: "Could not load the historical chart.",
      rateUnavailable: "Could not get the exchange rate.",
      longHistoryUnavailable: "The chart loaded, but the longer history for the estimated outlook is unavailable.",
      connectApi: "Could not connect to the Frankfurter API."
    }
  }
};

function getCurrentLocaleTag() {
  return appState.locale === "en" ? "en-US" : "ru-RU";
}

function createFormatters(locale) {
  return {
    amount: new Intl.NumberFormat(locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }),
    result: new Intl.NumberFormat(locale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }),
    rate: new Intl.NumberFormat(locale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    }),
    timestamp: new Intl.DateTimeFormat(locale, {
      dateStyle: "long",
      timeStyle: "short"
    }),
    apiDate: new Intl.DateTimeFormat(locale, {
      dateStyle: "long"
    }),
    chartDate: new Intl.DateTimeFormat(locale, {
      day: "2-digit",
      month: "short"
    })
  };
}

function createCurrencyDisplayNames(locale) {
  if (typeof Intl === "undefined" || typeof Intl.DisplayNames !== "function") {
    return null;
  }

  try {
    return new Intl.DisplayNames([locale], { type: "currency" });
  } catch (error) {
    return null;
  }
}

let formatters = createFormatters(getCurrentLocaleTag());
let currencyDisplayNames = createCurrencyDisplayNames(getCurrentLocaleTag());

function getTranslationValue(key) {
  return key.split(".").reduce((result, part) => (result ? result[part] : undefined), translations[appState.locale]);
}

function t(key, params = {}) {
  const template = getTranslationValue(key);
  if (typeof template !== "string") {
    return key;
  }

  return template.replace(/\{(\w+)\}/g, (_, token) => String(params[token] ?? ""));
}

function applyStaticTranslations() {
  document.documentElement.lang = appState.locale;
  document.title = t("doc.title");

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-attr]").forEach((element) => {
    element.dataset.i18nAttr.split(";").forEach((entry) => {
      const trimmedEntry = entry.trim();
      if (!trimmedEntry) {
        return;
      }

      const separatorIndex = trimmedEntry.indexOf(":");
      if (separatorIndex === -1) {
        return;
      }

      const attribute = trimmedEntry.slice(0, separatorIndex).trim();
      const key = trimmedEntry.slice(separatorIndex + 1).trim();
      element.setAttribute(attribute, t(key));
    });
  });
}

function loadStoredLanguage() {
  try {
    const storedLanguage = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (storedLanguage === "ru" || storedLanguage === "en") {
      appState.locale = storedLanguage;
    }
  } catch (error) {
    // Ignore storage issues and keep the default locale.
  }
}

function persistLanguage() {
  try {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, appState.locale);
  } catch (error) {
    // Ignore storage issues.
  }
}

function syncLanguageButtons() {
  languageButtons.forEach((button) => {
    const isActive = button.dataset.language === appState.locale;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

function updateLocaleFormatters() {
  formatters = createFormatters(getCurrentLocaleTag());
  currencyDisplayNames = createCurrencyDisplayNames(getCurrentLocaleTag());
}

function refreshLocalizedUi() {
  updateLocaleFormatters();
  applyStaticTranslations();
  syncLanguageButtons();
  syncForecastModeButtons();
  copyForecastButton.textContent = t("forecast.copy");

  if (appState.currencies.length) {
    fillCurrencySelect(fromCurrencySelect, fromCurrencySelect.value);
    fillCurrencySelect(toCurrencySelect, toCurrencySelect.value);
  }

  updatePickerTrigger(fromCurrencySelect);
  updatePickerTrigger(toCurrencySelect);

  appState.pickers.forEach((picker) => {
    if (picker.root.classList.contains("is-open")) {
      renderPickerOptions(picker.select, picker.search.value);
    }
  });

  const rawAmount = amountInput.value.trim();
  const amount = sanitizeAmount(amountInput.value);
  const fromCurrency = fromCurrencySelect.value;
  const toCurrency = toCurrencySelect.value;

  if (amount === null) {
    if (rawAmount) {
      renderInvalidAmountState();
    } else {
      renderIdleState();
    }
  } else if (fromCurrency === toCurrency) {
    setLoadingSkeleton(false);
    resultValue.textContent = `${formatters.result.format(amount)} ${toCurrency}`;
    resultHint.textContent = t("status.sameCurrencyHint");
    rateLine.textContent = `1 ${fromCurrency} = 1 ${toCurrency}`;
    updatedLine.textContent = t("status.sameCurrencyUpdated", {
      updatedAt: formatters.timestamp.format(new Date())
    });
    setResultState("is-success", t("status.noRate"));
    setStatusState("is-neutral", t("status.sameCurrencyStatus"));
    liveBadge.textContent = t("status.sameCurrencyBadge");
  } else if (appState.latestRatePayload && appState.latestRatePayload.base === fromCurrency && appState.latestRatePayload.quote === toCurrency) {
    renderSuccessState(appState.latestRatePayload, amount, fromCurrency, toCurrency);
  } else if (resultState.classList.contains("is-loading")) {
    renderLoadingState();
  } else if (resultState.classList.contains("is-error")) {
    renderErrorState(t("errors.rateUnavailable"));
  } else {
    renderIdleState();
  }

  chartSubtitle.textContent = fromCurrency && toCurrency
    ? t("chart.pairSubtitle", { from: fromCurrency, to: toCurrency, range: getRangeLabel(appState.chartRangeDays) })
    : t("chart.defaultSubtitle");

  if (fromCurrency === toCurrency) {
    historyChart.innerHTML = "";
    updateChartMeta([]);
    resetForecast();
    setChartState("is-empty", t("chart.sameCurrency"));
    return;
  }

  if (appState.currentChartPoints.length) {
    renderHistoryChart(appState.currentChartPoints);
  } else if (chartStateBox.classList.contains("is-loading")) {
    setChartState("is-loading", t("chart.loading"));
  } else if (chartStateBox.classList.contains("is-error")) {
    setChartState("is-error", t("errors.chartUnavailable"));
  } else {
    setChartState("is-empty", t("chart.empty"));
  }

  if (appState.currentForecastPoints.length) {
    updateForecast(appState.currentForecastPoints);
  } else if (appState.currentChartPoints.length) {
    resetForecast();
    forecastSummary.textContent = t("errors.longHistoryUnavailable");
  } else if (!fromCurrency || !toCurrency || fromCurrency === toCurrency) {
    resetForecast();
  }
}

function setLanguage(nextLanguage) {
  if (nextLanguage !== "ru" && nextLanguage !== "en") {
    return;
  }

  if (nextLanguage === appState.locale) {
    return;
  }

  appState.locale = nextLanguage;
  persistLanguage();
  refreshLocalizedUi();
}

function getLocalizedCurrencyName(code, fallbackName = "") {
  const normalizedCode = String(code || "").toUpperCase();
  if (currencyDisplayNames && normalizedCode) {
    const localizedName = currencyDisplayNames.of(normalizedCode);
    if (localizedName && localizedName !== normalizedCode) {
      return localizedName;
    }
  }

  return fallbackName || normalizedCode;
}

function getCurrencyDisplayParts(currency) {
  const primaryName = getLocalizedCurrencyName(currency.code, currency.name);
  const secondaryParts = [];

  if (currency.name && currency.name !== primaryName) {
    secondaryParts.push(currency.name);
  }

  if (currency.symbol) {
    secondaryParts.push(currency.symbol);
  }

  return {
    primaryName,
    secondaryMeta: secondaryParts.join(" · ")
  };
}

function getCurrencyLabel(code) {
  const currency = appState.currencyMap.get(code);
  if (!currency) {
    return code;
  }

  return `${code} · ${getCurrencyDisplayParts(currency).primaryName}`;
}

function setStatusState(type, text) {
  statusBox.className = `status-box ${type}`;
  statusBox.textContent = text;
}

function setResultState(type, text) {
  resultState.className = `result-state ${type}`;
  resultState.textContent = text;
}

function setLoadingSkeleton(isLoading) {
  [resultValue, rateLine, updatedLine].forEach((element) => {
    element.classList.toggle("is-skeleton", isLoading);
  });
}

function setChartState(type, text) {
  chartStateBox.className = `chart-state ${type}`;
  chartStateBox.textContent = text;
}

function triggerSwapAnimation() {
  swapButton.classList.remove("is-swapping");
  void swapButton.offsetWidth;
  swapButton.classList.add("is-swapping");
}

function sanitizeAmount(value) {
  if (!value.trim()) {
    return null;
  }

  const normalized = Number(value);
  if (!Number.isFinite(normalized) || normalized < 0) {
    return null;
  }

  return normalized;
}

function fillCurrencySelect(selectElement, preferredCode) {
  selectElement.innerHTML = "";

  appState.currencies.forEach((currency) => {
    const option = document.createElement("option");
    option.value = currency.code;
    option.textContent = getCurrencyLabel(currency.code);
    option.selected = currency.code === preferredCode;
    selectElement.append(option);
  });
}

function getPickerInstanceBySelect(selectElement) {
  return appState.pickers.get(selectElement.id);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatIsoDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function subtractDays(days) {
  const date = new Date();
  date.setHours(0, 0, 0, 0);
  date.setDate(date.getDate() - days);
  return date;
}

function mean(values) {
  if (!values.length) {
    return 0;
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function standardDeviation(values) {
  if (values.length < 2) {
    return 0;
  }

  const average = mean(values);
  const variance = mean(values.map((value) => (value - average) ** 2));
  return Math.sqrt(variance);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function quantile(values, percentile) {
  if (!values.length) {
    return 0;
  }

  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * percentile;
  const lowerIndex = Math.floor(position);
  const upperIndex = Math.min(lowerIndex + 1, sorted.length - 1);
  const interpolation = position - lowerIndex;

  return sorted[lowerIndex] + (sorted[upperIndex] - sorted[lowerIndex]) * interpolation;
}

function winsorizeSeries(values, lowerQuantile = 0.08, upperQuantile = 0.92) {
  if (values.length < 6) {
    return values.slice();
  }

  const lowerBound = quantile(values, lowerQuantile);
  const upperBound = quantile(values, upperQuantile);
  return values.map((value) => clamp(value, lowerBound, upperBound));
}

function calculateEwmaMean(values, lambda) {
  if (!values.length) {
    return 0;
  }

  let result = values[0];
  for (let index = 1; index < values.length; index += 1) {
    result = lambda * result + (1 - lambda) * values[index];
  }
  return result;
}

function calculateEwmaVariance(values, lambda) {
  if (!values.length) {
    return 0;
  }

  let variance = values[0] ** 2;
  for (let index = 1; index < values.length; index += 1) {
    variance = lambda * variance + (1 - lambda) * (values[index] ** 2);
  }
  return variance;
}

function calculateEwmaLevel(values, lambda) {
  if (!values.length) {
    return 0;
  }

  let level = values[0];
  for (let index = 1; index < values.length; index += 1) {
    level = lambda * level + (1 - lambda) * values[index];
  }
  return level;
}

function getRangeLabel(days) {
  if (days === 7) {
    return t("chart.rangeLabelWeek");
  }

  if (days === 30) {
    return t("chart.rangeLabelMonth");
  }

  if (days === 365) {
    return t("chart.rangeLabelYear");
  }

  return t("chart.rangeLabelDays", { days });
}

function highlightMatch(value, query) {
  const safeValue = escapeHtml(value);
  const normalizedQuery = query.trim();
  if (!normalizedQuery) {
    return safeValue;
  }

  const index = value.toLowerCase().indexOf(normalizedQuery.toLowerCase());
  if (index === -1) {
    return safeValue;
  }

  const before = escapeHtml(value.slice(0, index));
  const match = escapeHtml(value.slice(index, index + normalizedQuery.length));
  const after = escapeHtml(value.slice(index + normalizedQuery.length));
  return `${before}<mark class="currency-match">${match}</mark>${after}`;
}

function updatePickerTrigger(selectElement) {
  const picker = getPickerInstanceBySelect(selectElement);
  if (!picker) {
    return;
  }

  const currency = appState.currencyMap.get(selectElement.value);
  if (!currency) {
    picker.code.textContent = "---";
    picker.name.textContent = t("converter.chooseCurrency");
    picker.trigger.setAttribute("aria-label", t("converter.chooseCurrency"));
    return;
  }

  const { primaryName } = getCurrencyDisplayParts(currency);
  picker.code.textContent = currency.code;
  picker.name.textContent = primaryName;
  picker.trigger.setAttribute("aria-label", `${currency.code} ${primaryName}`);
}

function buildOptionMarkup(currency, query) {
  const { primaryName, secondaryMeta } = getCurrencyDisplayParts(currency);
  const metaMarkup = secondaryMeta ? highlightMatch(secondaryMeta, query) : "";

  return `
    <span class="currency-option__title">${highlightMatch(currency.code, query)} · ${highlightMatch(primaryName, query)}</span>
    <span class="currency-option__meta">${metaMarkup}</span>
  `;
}

function setHighlightedOption(picker, nextIndex) {
  const options = Array.from(picker.options.querySelectorAll(".currency-option"));
  if (!options.length) {
    picker.highlightedIndex = -1;
    return;
  }

  const normalizedIndex = Math.max(0, Math.min(nextIndex, options.length - 1));
  picker.highlightedIndex = normalizedIndex;

  options.forEach((option, index) => {
    option.classList.toggle("is-highlighted", index === normalizedIndex);
  });

  options[normalizedIndex].scrollIntoView({ block: "nearest" });
}

function updateChartMeta(points) {
  if (!points.length) {
    chartMin.textContent = "-";
    chartMax.textContent = "-";
    chartLatest.textContent = "-";
    return;
  }

  const rates = points.map((point) => point.rate);
  const latestPoint = points[points.length - 1];
  chartMin.textContent = `${formatters.rate.format(Math.min(...rates))} ${latestPoint.quote}`;
  chartMax.textContent = `${formatters.rate.format(Math.max(...rates))} ${latestPoint.quote}`;
  chartLatest.textContent = `${formatters.rate.format(latestPoint.rate)} ${latestPoint.quote}`;
}

function getForecastModeConfig() {
  if (appState.forecastMode === "aggressive") {
    return {
      short: 0.46,
      medium: 0.28,
      long: 0.11,
      reversion: 0.15,
      damping: 0.9,
      band: 1.12,
      maxShrink: 0.88,
      title: t("forecast.modeAggressive")
    };
  }

  if (appState.forecastMode === "neutral") {
    return {
      short: 0.38,
      medium: 0.28,
      long: 0.14,
      reversion: 0.2,
      damping: 0.72,
      band: 1,
      maxShrink: 0.72,
      title: t("forecast.modeNeutral")
    };
  }

  return {
    short: 0.32,
    medium: 0.26,
    long: 0.16,
    reversion: 0.26,
    damping: 0.56,
    band: 0.92,
    maxShrink: 0.56,
    title: t("forecast.modeConservative")
  };
}

function buildForecastFeatureSet(rates, logReturns) {
  const signalReturns = winsorizeSeries(logReturns.slice(-Math.min(220, logReturns.length)), 0.08, 0.92);
  const volatilityReturns = winsorizeSeries(logReturns.slice(-Math.min(220, logReturns.length)), 0.04, 0.96);
  const shortWindow = signalReturns.slice(-Math.min(12, signalReturns.length));
  const mediumWindow = signalReturns.slice(-Math.min(36, signalReturns.length));
  const longWindow = signalReturns.slice(-Math.min(120, signalReturns.length));
  const levelWindow = rates.slice(-Math.min(220, rates.length));
  const shortMean = calculateEwmaMean(shortWindow, 0.78);
  const mediumMean = calculateEwmaMean(mediumWindow, 0.9);
  const longMean = calculateEwmaMean(longWindow, 0.97);
  const anchorLevel = calculateEwmaLevel(levelWindow, 0.988);
  const meanReversion = Math.log(anchorLevel / rates[rates.length - 1]) / 45;
  const ewmaVolatility = Math.sqrt(calculateEwmaVariance(volatilityReturns.slice(-Math.min(180, volatilityReturns.length)), 0.94));

  return {
    shortMean,
    mediumMean,
    longMean,
    meanReversion,
    ewmaVolatility
  };
}

function calculateAdaptiveForecastCalibration(rates, logReturns, modeConfig) {
  const candidateNames = ["short", "medium", "long", "reversion"];
  const priorWeights = {
    short: modeConfig.short,
    medium: modeConfig.medium,
    long: modeConfig.long,
    reversion: modeConfig.reversion
  };
  const fallbackWeightSum = candidateNames.reduce((sum, name) => sum + priorWeights[name], 0);
  const fallbackWeights = candidateNames.reduce((result, name) => {
    result[name] = priorWeights[name] / fallbackWeightSum;
    return result;
  }, {});
  const evaluationWindow = [];

  for (let nextReturnIndex = Math.max(55, logReturns.length - 75); nextReturnIndex < logReturns.length; nextReturnIndex += 1) {
    const knownRates = rates.slice(0, nextReturnIndex + 1);
    const knownReturns = logReturns.slice(0, nextReturnIndex);
    if (knownReturns.length < 55) {
      continue;
    }

    const features = buildForecastFeatureSet(knownRates, knownReturns);
    const actualReturn = logReturns[nextReturnIndex];
    const candidates = {
      short: features.shortMean,
      medium: features.mediumMean,
      long: features.longMean,
      reversion: features.meanReversion
    };

    evaluationWindow.push({
      actualReturn,
      candidates
    });
  }

  if (evaluationWindow.length < 14) {
    return {
      weights: fallbackWeights,
      hitRate: 0.5,
      skillLift: 0,
      sampleSize: evaluationWindow.length
    };
  }

  const splitIndex = Math.max(10, Math.floor(evaluationWindow.length * 0.6));
  const calibrationWindow = evaluationWindow.slice(0, splitIndex);
  const validationWindow = evaluationWindow.slice(splitIndex);
  const squaredErrors = {
    short: [],
    medium: [],
    long: [],
    reversion: []
  };

  calibrationWindow.forEach(({ actualReturn, candidates }) => {
    candidateNames.forEach((name) => {
      squaredErrors[name].push((candidates[name] - actualReturn) ** 2);
    });
  });

  const weights = candidateNames.reduce((result, name) => {
    const rmse = Math.sqrt(mean(squaredErrors[name]));
    result[name] = priorWeights[name] / Math.max(rmse, 1e-6);
    return result;
  }, {});
  const weightSum = candidateNames.reduce((sum, name) => sum + weights[name], 0);

  candidateNames.forEach((name) => {
    weights[name] /= weightSum;
  });

  const ensembleErrors = [];
  let directionalHits = 0;
  const benchmarkWindow = validationWindow.length >= 6 ? validationWindow : evaluationWindow;

  benchmarkWindow.forEach(({ actualReturn, candidates }) => {
    const predictedReturn = candidateNames.reduce((sum, name) => sum + weights[name] * candidates[name], 0);
    ensembleErrors.push((predictedReturn - actualReturn) ** 2);

    if (Math.abs(predictedReturn) < 1e-6 || Math.abs(actualReturn) < 1e-6 || Math.sign(predictedReturn) === Math.sign(actualReturn)) {
      directionalHits += 1;
    }
  });

  const baselineRmse = Math.sqrt(mean(benchmarkWindow.map((point) => point.actualReturn ** 2)));
  const ensembleRmse = Math.sqrt(mean(ensembleErrors));
  const skillLift = baselineRmse > 0
    ? clamp((baselineRmse - ensembleRmse) / baselineRmse, -0.18, 0.24)
    : 0;

  return {
    weights,
    hitRate: directionalHits / benchmarkWindow.length,
    skillLift,
    sampleSize: evaluationWindow.length
  };
}

function loadStoredForecastMode() {
  try {
    const storedMode = window.localStorage.getItem(FORECAST_MODE_STORAGE_KEY);
    if (storedMode === "conservative" || storedMode === "neutral" || storedMode === "aggressive") {
      appState.forecastMode = storedMode;
    }
  } catch (error) {
    // Ignore storage access issues and keep the default mode.
  }
}

function persistForecastMode() {
  try {
    window.localStorage.setItem(FORECAST_MODE_STORAGE_KEY, appState.forecastMode);
  } catch (error) {
    // Ignore storage access issues.
  }
}

function syncForecastModeButtons() {
  forecastModeButtons.forEach((button) => {
    const isActive = button.dataset.forecastMode === appState.forecastMode;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

function resetForecast() {
  forecastDirection.className = "forecast-badge is-neutral";
  forecastDirection.textContent = t("forecast.awaiting");
  forecastDeltaLine.className = "forecast-delta-line is-neutral";
  forecastSpot.textContent = "-";
  forecastSpotContext.textContent = "-";
  forecastTomorrowCard.className = "forecast-metric forecast-metric--horizon";
  forecastTomorrow.textContent = "-";
  forecastTomorrowDelta.textContent = "-";
  forecastTomorrowRange.textContent = "-";
  forecastWeekCard.className = "forecast-metric forecast-metric--horizon";
  forecastMonthCard.className = "forecast-metric forecast-metric--horizon forecast-metric--month";
  forecastWeek.textContent = "-";
  forecastWeekDelta.textContent = "-";
  forecastWeekRange.textContent = "-";
  forecastMonth.textContent = "-";
  forecastMonthDelta.textContent = "-";
  forecastMonthRange.textContent = "-";
  forecastConfidence.textContent = "-";
  forecastContext.textContent = "-";
  forecastSignalStrength.textContent = "-";
  forecastVolatility.textContent = "-";
  forecastMode.textContent = "-";
  copyForecastButton.textContent = t("forecast.copy");
  forecastSummary.textContent = t("forecast.summaryDefault");
  forecastDeltaLine.textContent = t("forecast.deltaDefault");
  forecastReason.textContent = t("forecast.reasonDefault");
  forecastInsight.textContent = t("forecast.insightDefault");
}

function getForecastTrendSymbol(deltaPercent, threshold) {
  if (Math.abs(deltaPercent) < threshold) {
    return "→";
  }

  return deltaPercent > 0 ? "↑" : "↓";
}

function buildForecastValueMarkup(rate, quote, deltaPercent, threshold) {
  const trendSymbol = getForecastTrendSymbol(deltaPercent, threshold);

  return `<span class="forecast-trend">${trendSymbol}</span> <span class="forecast-value-number">${formatters.rate.format(rate)}</span> <span class="forecast-value-code">${quote}</span>`;
}

function updateForecast(points) {
  if (points.length < 60) {
    resetForecast();
    forecastSummary.textContent = t("forecast.notEnoughHistory");
    return;
  }

  const latest = points[points.length - 1];
  const rates = points.map((point) => point.rate);
  const logReturns = [];

  for (let index = 1; index < rates.length; index += 1) {
    logReturns.push(Math.log(rates[index] / rates[index - 1]));
  }

  const modeConfig = getForecastModeConfig();

  const featureSet = buildForecastFeatureSet(rates, logReturns);
  const calibration = calculateAdaptiveForecastCalibration(rates, logReturns, modeConfig);
  const priorSignal = featureSet.shortMean * modeConfig.short
    + featureSet.mediumMean * modeConfig.medium
    + featureSet.longMean * modeConfig.long
    + featureSet.meanReversion * modeConfig.reversion;
  const adaptiveSignal = featureSet.shortMean * calibration.weights.short
    + featureSet.mediumMean * calibration.weights.medium
    + featureSet.longMean * calibration.weights.long
    + featureSet.meanReversion * calibration.weights.reversion;
  const rawSignal = priorSignal * 0.42 + adaptiveSignal * 0.58;
  const directionalAgreement = mean([
    Math.sign(featureSet.shortMean) === Math.sign(featureSet.mediumMean) || Math.abs(featureSet.shortMean) < 1e-6 || Math.abs(featureSet.mediumMean) < 1e-6 ? 1 : 0.72,
    Math.sign(featureSet.mediumMean) === Math.sign(featureSet.longMean) || Math.abs(featureSet.mediumMean) < 1e-6 || Math.abs(featureSet.longMean) < 1e-6 ? 1 : 0.8
  ]);
  const signalToNoise = Math.abs(rawSignal) / Math.max(featureSet.ewmaVolatility, 1e-6);
  const shrinkage = clamp(
    (0.08 + signalToNoise * 0.32 + calibration.skillLift * 0.55 + (calibration.hitRate - 0.5) * 0.4) * directionalAgreement,
    0.06,
    modeConfig.maxShrink
  );
  const dailySignal = rawSignal * modeConfig.damping * shrinkage;

  const projectRate = (days) => latest.rate * Math.exp(dailySignal * days);
  const projectBand = (days) => {
    const sigma = featureSet.ewmaVolatility * Math.sqrt(days) * modeConfig.band;
    return {
      lower: latest.rate * Math.exp((dailySignal - sigma) * days),
      upper: latest.rate * Math.exp((dailySignal + sigma) * days)
    };
  };

  const tomorrowRate = projectRate(1);
  const tomorrowBand = projectBand(1);
  const weekRate = projectRate(7);
  const monthRate = projectRate(30);
  const weekBand = projectBand(7);
  const monthBand = projectBand(30);
  const tomorrowDeltaPercent = ((tomorrowRate / latest.rate) - 1) * 100;
  const weekDeltaPercent = ((weekRate / latest.rate) - 1) * 100;
  const deltaPercent = ((monthRate / latest.rate) - 1) * 100;
  const confidenceScore = Math.round(clamp(
    26
      + signalToNoise * 16
      + directionalAgreement * 12
      + calibration.skillLift * 70
      + (calibration.hitRate - 0.5) * 42
      - featureSet.ewmaVolatility * 1250,
    16,
    84
  ));
  const signalMetric = signalToNoise * (1 + calibration.skillLift);
  const signalStrength = signalMetric < 0.24 ? t("forecast.signalLow") : signalMetric < 0.58 ? t("forecast.signalMedium") : t("forecast.signalHigh");
  const volatilityLabel = featureSet.ewmaVolatility < 0.004 ? t("forecast.volatilityCalm") : featureSet.ewmaVolatility < 0.009 ? t("forecast.volatilityModerate") : t("forecast.volatilityHigh");
  const modeLabel = Math.abs(deltaPercent) < 0.35
    ? t("forecast.biasSideways")
    : deltaPercent > 0
      ? t("forecast.biasUp")
      : t("forecast.biasDown");

  let directionText = t("forecast.directionSideways");
  let directionClass = "is-sideways";

  if (deltaPercent > 0.35) {
    directionText = t("forecast.directionUp");
    directionClass = "is-up";
  } else if (deltaPercent < -0.35) {
    directionText = t("forecast.directionDown");
    directionClass = "is-down";
  }

  forecastDirection.className = `forecast-badge ${directionClass}`;
  forecastDirection.textContent = directionText;
  forecastDeltaLine.className = `forecast-delta-line ${directionClass}`;
  forecastSpot.textContent = `${formatters.rate.format(latest.rate)} ${latest.quote}`;
  forecastSpotContext.textContent = t("forecast.spotContext", {
    base: latest.base,
    rate: formatters.rate.format(latest.rate),
    quote: latest.quote
  });
  forecastTomorrowCard.className = `forecast-metric forecast-metric--horizon ${Math.abs(tomorrowDeltaPercent) < 0.12 ? "is-sideways" : tomorrowDeltaPercent > 0 ? "is-up" : "is-down"}`;
  forecastTomorrow.innerHTML = buildForecastValueMarkup(tomorrowRate, latest.quote, tomorrowDeltaPercent, 0.12);
  forecastTomorrowDelta.textContent = t("forecast.deltaVsCurrent", {
    value: `${tomorrowDeltaPercent >= 0 ? "+" : ""}${tomorrowDeltaPercent.toFixed(2)}%`
  });
  forecastTomorrowRange.textContent = t("forecast.range", {
    lower: formatters.rate.format(tomorrowBand.lower),
    upper: formatters.rate.format(tomorrowBand.upper),
    quote: latest.quote
  });
  forecastWeekCard.className = `forecast-metric forecast-metric--horizon ${Math.abs(weekDeltaPercent) < 0.25 ? "is-sideways" : weekDeltaPercent > 0 ? "is-up" : "is-down"}`;
  forecastMonthCard.className = `forecast-metric forecast-metric--horizon forecast-metric--month ${directionClass}`;
  forecastWeek.innerHTML = buildForecastValueMarkup(weekRate, latest.quote, weekDeltaPercent, 0.25);
  forecastWeekDelta.textContent = t("forecast.deltaVsCurrent", {
    value: `${weekDeltaPercent >= 0 ? "+" : ""}${weekDeltaPercent.toFixed(2)}%`
  });
  forecastWeekRange.textContent = t("forecast.range", {
    lower: formatters.rate.format(weekBand.lower),
    upper: formatters.rate.format(weekBand.upper),
    quote: latest.quote
  });
  forecastMonth.innerHTML = buildForecastValueMarkup(monthRate, latest.quote, deltaPercent, 0.35);
  forecastMonthDelta.textContent = t("forecast.deltaVsCurrent", {
    value: `${deltaPercent >= 0 ? "+" : ""}${deltaPercent.toFixed(2)}%`
  });
  forecastMonthRange.textContent = t("forecast.range", {
    lower: formatters.rate.format(monthBand.lower),
    upper: formatters.rate.format(monthBand.upper),
    quote: latest.quote
  });
  forecastConfidence.textContent = `${confidenceScore}%`;
  forecastContext.textContent = t("forecast.context", { sample: calibration.sampleSize });
  forecastSignalStrength.textContent = signalStrength;
  forecastVolatility.textContent = volatilityLabel;
  forecastMode.textContent = `${modeConfig.title} · ${modeLabel}`;
  forecastSummary.textContent = t("forecast.summaryDynamic", {
    from: latest.base,
    to: latest.quote
  });
  forecastDeltaLine.textContent = t("forecast.deltaDynamic", {
    value: `${deltaPercent >= 0 ? "+" : ""}${deltaPercent.toFixed(2)}%`
  });
  forecastReason.textContent =
    Math.abs(deltaPercent) < 0.35
      ? t("forecast.reasonSideways")
      : deltaPercent > 0
        ? t("forecast.reasonUp")
        : t("forecast.reasonDown");
  forecastInsight.textContent =
    Math.abs(deltaPercent) < 0.35
      ? t("forecast.insightSideways", { pair: `${latest.base}/${latest.quote}` })
      : deltaPercent > 0
        ? t("forecast.insightUp", { pair: `${latest.base}/${latest.quote}` })
        : t("forecast.insightDown", { pair: `${latest.base}/${latest.quote}` });
}

function renderHistoryChart(points) {
  if (!points.length) {
    historyChart.innerHTML = "";
    updateChartMeta([]);
    setChartState("is-empty", t("chart.empty"));
    return;
  }

  const width = 760;
  const height = 320;
  const padding = { top: 24, right: 22, bottom: 34, left: 22 };
  const rates = points.map((point) => point.rate);
  const minRate = Math.min(...rates);
  const maxRate = Math.max(...rates);
  const spread = Math.max(maxRate - minRate, maxRate * 0.015 || 1);
  const visualMin = minRate - spread * 0.18;
  const visualMax = maxRate + spread * 0.12;
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const xStep = points.length > 1 ? innerWidth / (points.length - 1) : 0;
  const yForRate = (rate) => padding.top + ((visualMax - rate) / (visualMax - visualMin)) * innerHeight;

  const coordinates = points.map((point, index) => ({
    ...point,
    x: padding.left + xStep * index,
    y: yForRate(point.rate)
  }));

  const linePath = coordinates
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
    .join(" ");
  const areaPath = `${linePath} L ${coordinates[coordinates.length - 1].x.toFixed(2)} ${(height - padding.bottom).toFixed(2)} L ${coordinates[0].x.toFixed(2)} ${(height - padding.bottom).toFixed(2)} Z`;
  const latestPoint = coordinates[coordinates.length - 1];
  const minPoint = coordinates.reduce((acc, point) => (point.rate < acc.rate ? point : acc), coordinates[0]);
  const maxPoint = coordinates.reduce((acc, point) => (point.rate > acc.rate ? point : acc), coordinates[0]);
  const dateLabelIndexes = Array.from(new Set([0, Math.floor((coordinates.length - 1) / 2), coordinates.length - 1]));
  const gridRates = [visualMax, (visualMax + visualMin) / 2, visualMin];

  historyChart.innerHTML = `
    <defs>
      <linearGradient id="chartAreaGradient" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgba(99, 216, 192, 0.34)"></stop>
        <stop offset="100%" stop-color="rgba(99, 216, 192, 0)"></stop>
      </linearGradient>
    </defs>
    ${gridRates.map((rate) => `<line class="chart-grid-line" x1="${padding.left}" y1="${yForRate(rate).toFixed(2)}" x2="${width - padding.right}" y2="${yForRate(rate).toFixed(2)}"></line>`).join("")}
    <path class="chart-area" d="${areaPath}"></path>
    <path class="chart-line" d="${linePath}"></path>
    ${coordinates.map((point, index) => `<circle class="chart-point ${index === coordinates.length - 1 ? "chart-point--latest" : ""}" cx="${point.x.toFixed(2)}" cy="${point.y.toFixed(2)}" r="${index === coordinates.length - 1 ? 6 : 3.1}"></circle>`).join("")}
    ${dateLabelIndexes.map((index) => {
      const point = coordinates[index];
      const anchor = index === 0 ? "start" : index === coordinates.length - 1 ? "end" : "middle";
      return `<text class="chart-axis-label" x="${point.x.toFixed(2)}" y="${height - 8}" text-anchor="${anchor}">${formatters.chartDate.format(new Date(point.date))}</text>`;
    }).join("")}
    <text class="chart-minmax" x="${maxPoint.x.toFixed(2)}" y="${(maxPoint.y - 12).toFixed(2)}" text-anchor="middle">${t("chart.peak")} ${formatters.rate.format(maxPoint.rate)}</text>
    <text class="chart-minmax" x="${minPoint.x.toFixed(2)}" y="${(minPoint.y + 22).toFixed(2)}" text-anchor="middle">${t("chart.low")} ${formatters.rate.format(minPoint.rate)}</text>
    <text class="chart-point-label" x="${latestPoint.x.toFixed(2)}" y="${(latestPoint.y - 16).toFixed(2)}" text-anchor="end">${t("chart.now")} ${formatters.rate.format(latestPoint.rate)}</text>
  `;

  updateChartMeta(points);
  chartStateBox.className = "chart-state";
  chartStateBox.textContent = "";
}

function renderPickerOptions(selectElement, query = "") {
  const picker = getPickerInstanceBySelect(selectElement);
  if (!picker) {
    return;
  }

  const normalizedQuery = query.trim().toLowerCase();
  const filteredCurrencies = appState.currencies.filter((currency) => {
    if (!normalizedQuery) {
      return true;
    }

    const { primaryName } = getCurrencyDisplayParts(currency);
    return [
      currency.code,
      primaryName,
      currency.name,
      currency.symbol
    ]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(normalizedQuery));
  });

  picker.options.innerHTML = "";
  picker.highlightedIndex = -1;

  if (!filteredCurrencies.length) {
    const emptyState = document.createElement("div");
    emptyState.className = "currency-empty";
    emptyState.textContent = t("picker.empty");
    picker.options.append(emptyState);
    return;
  }

  filteredCurrencies.forEach((currency) => {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "currency-option";
    option.innerHTML = buildOptionMarkup(currency, normalizedQuery);
    option.dataset.code = currency.code;
    option.setAttribute("role", "option");
    option.setAttribute("aria-selected", String(selectElement.value === currency.code));

    if (selectElement.value === currency.code) {
      option.classList.add("is-active");
    }

    option.addEventListener("click", () => {
      selectElement.value = currency.code;
      updatePickerTrigger(selectElement);
      closePicker(picker);
      recalculate();
      updateHistoricalChart();
    });

    picker.options.append(option);
  });

  const selectedIndex = filteredCurrencies.findIndex((currency) => currency.code === selectElement.value);
  setHighlightedOption(picker, selectedIndex >= 0 ? selectedIndex : 0);
}

function closePicker(picker) {
  picker.root.classList.remove("is-open");
  picker.dropdown.hidden = true;
  picker.trigger.setAttribute("aria-expanded", "false");
  picker.search.value = "";
}

function closeAllPickers(exceptId = null) {
  appState.pickers.forEach((picker, key) => {
    if (key !== exceptId) {
      closePicker(picker);
    }
  });
}

function openPicker(selectElement, focusSearch) {
  const picker = getPickerInstanceBySelect(selectElement);
  if (!picker) {
    return;
  }

  closeAllPickers(selectElement.id);
  picker.root.classList.add("is-open");
  picker.dropdown.hidden = false;
  picker.trigger.setAttribute("aria-expanded", "true");
  renderPickerOptions(selectElement, focusSearch ? picker.search.value : "");

  if (focusSearch) {
    picker.search.focus();
    picker.search.select();
  }
}

function setupPicker(selectElement) {
  const root = selectElement.closest(".currency-picker");
  const picker = {
    root,
    select: selectElement,
    trigger: root.querySelector('[data-role="trigger"]'),
    arrow: root.querySelector('[data-role="arrow"]'),
    dropdown: root.querySelector('[data-role="dropdown"]'),
    search: root.querySelector('[data-role="search"]'),
    options: root.querySelector('[data-role="options"]'),
    code: root.querySelector('[data-role="code"]'),
    name: root.querySelector('[data-role="name"]'),
    highlightedIndex: -1
  };

  appState.pickers.set(selectElement.id, picker);

  picker.trigger.addEventListener("click", () => {
    const isOpen = picker.root.classList.contains("is-open");
    if (isOpen) {
      picker.search.focus();
      picker.search.select();
      return;
    }

    openPicker(selectElement, true);
  });

  picker.arrow.addEventListener("click", () => {
    const isOpen = picker.root.classList.contains("is-open");
    if (isOpen) {
      if (picker.search.value.trim()) {
        picker.search.value = "";
        renderPickerOptions(selectElement, "");
        return;
      }

      closePicker(picker);
      return;
    }

    picker.search.value = "";
    openPicker(selectElement, false);
  });

  picker.search.addEventListener("input", () => {
    renderPickerOptions(selectElement, picker.search.value);
  });

  picker.search.addEventListener("keydown", (event) => {
    const options = Array.from(picker.options.querySelectorAll(".currency-option"));

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setHighlightedOption(picker, picker.highlightedIndex + 1);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setHighlightedOption(picker, picker.highlightedIndex - 1);
      return;
    }

    if (event.key === "Enter") {
      const activeOption = options[picker.highlightedIndex];
      if (activeOption) {
        event.preventDefault();
        activeOption.click();
      }
    }
  });
}

async function fetchCurrencies() {
  const response = await fetch(`${API_BASE_URL}/currencies`);
  if (!response.ok) {
    throw new Error(t("errors.loadCurrencies"));
  }

  const currencies = await response.json();
  return currencies
    .map((item) => ({
      code: item.iso_code,
      name: item.name,
      symbol: item.symbol || ""
    }))
    .sort((left, right) => left.code.localeCompare(right.code, "en"));
}

async function fetchHistoricalRates(fromCurrency, toCurrency, days) {
  const cacheKey = `${fromCurrency}:${toCurrency}:${days}`;
  if (appState.historyCache.has(cacheKey)) {
    return appState.historyCache.get(cacheKey);
  }

  const url = new URL(`${API_BASE_URL}/rates`);
  url.searchParams.set("from", formatIsoDate(subtractDays(days - 1)));
  url.searchParams.set("to", formatIsoDate(new Date()));
  url.searchParams.set("base", fromCurrency);
  url.searchParams.set("quotes", toCurrency);

  const request = fetch(url.toString())
    .then((response) => {
      if (!response.ok) {
        throw new Error(t("errors.loadHistorical"));
      }

      return response.json();
    })
    .catch((error) => {
      appState.historyCache.delete(cacheKey);
      throw error;
    });

  appState.historyCache.set(cacheKey, request);
  return request;
}

function buildRateUrl(fromCurrency, toCurrency) {
  const url = new URL(`${API_BASE_URL}/rates`);
  url.searchParams.set("base", fromCurrency);
  url.searchParams.set("quotes", toCurrency);
  return url.toString();
}

async function fetchRate(fromCurrency, toCurrency) {
  const response = await fetch(buildRateUrl(fromCurrency, toCurrency));
  if (!response.ok) {
    throw new Error(t("errors.loadLatestRate"));
  }

  const [payload] = await response.json();
  if (!payload || typeof payload.rate !== "number") {
    throw new Error(t("errors.incompleteRate"));
  }

  return payload;
}

function renderIdleState() {
  appState.latestRatePayload = null;
  resultValue.textContent = t("status.idleValue");
  resultHint.textContent = t("status.idleHint");
  rateLine.textContent = `1 ${fromCurrencySelect.value} = ? ${toCurrencySelect.value}`;
  updatedLine.textContent = t("status.idleUpdated");
  setResultState("is-idle", t("status.waiting"));
  setStatusState("is-neutral", t("status.ready"));
  liveBadge.textContent = t("status.awaitingInput");
}

function renderInvalidAmountState() {
  appState.latestRatePayload = null;
  setLoadingSkeleton(false);
  resultValue.textContent = t("status.invalidValue");
  resultHint.textContent = t("status.invalidHint");
  rateLine.textContent = `1 ${fromCurrencySelect.value} = ? ${toCurrencySelect.value}`;
  updatedLine.textContent = t("status.invalidUpdated");
  setResultState("is-error", t("status.invalidState"));
  setStatusState("is-error", t("status.invalidStatus"));
  liveBadge.textContent = t("status.inputErrorBadge");
}

function renderLoadingState() {
  appState.latestRatePayload = null;
  setLoadingSkeleton(true);
  resultValue.textContent = t("status.loadingValue");
  resultHint.textContent = t("status.loadingHint");
  rateLine.textContent = t("status.loadingRate");
  updatedLine.textContent = t("status.loadingUpdated");
  setResultState("is-loading", t("status.loadingState"));
  setStatusState("is-loading", t("status.loadingStatus"));
  liveBadge.textContent = t("status.loadingBadge");
}

function renderErrorState(message) {
  appState.latestRatePayload = null;
  setLoadingSkeleton(false);
  resultValue.textContent = t("status.errorValue");
  resultHint.textContent = t("status.errorHint");
  setResultState("is-error", t("status.errorState"));
  setStatusState("is-error", message);
  liveBadge.textContent = t("status.apiErrorBadge");
}

function renderSuccessState(payload, amount, fromCurrency, toCurrency) {
  appState.latestRatePayload = payload;
  const convertedAmount = amount * payload.rate;
  const updatedAt = formatters.timestamp.format(new Date());
  const apiDate = payload.date ? formatters.apiDate.format(new Date(payload.date)) : null;

  setLoadingSkeleton(false);
  resultValue.textContent = `${formatters.result.format(convertedAmount)} ${toCurrency}`;
  resultHint.textContent = t("status.resultHint", {
    amount: formatters.amount.format(amount),
    from: fromCurrency,
    to: toCurrency
  });
  rateLine.textContent = `1 ${fromCurrency} = ${formatters.rate.format(payload.rate)} ${toCurrency}`;
  updatedLine.textContent = apiDate
    ? t("status.updatedWithDate", { date: apiDate, updatedAt })
    : t("status.updatedWithoutDate", { updatedAt });
  setResultState("is-success", t("status.successState"));
  setStatusState("is-live", t("status.successStatus"));
  liveBadge.textContent = t("status.successBadge");
}

async function updateHistoricalChart() {
  const fromCurrency = fromCurrencySelect.value;
  const toCurrency = toCurrencySelect.value;

  if (!fromCurrency || !toCurrency) {
    return;
  }

  chartSubtitle.textContent = t("chart.pairSubtitle", {
    from: fromCurrency,
    to: toCurrency,
    range: getRangeLabel(appState.chartRangeDays)
  });

  if (fromCurrency === toCurrency) {
    appState.currentChartPoints = [];
    appState.currentForecastPoints = [];
    historyChart.innerHTML = "";
    updateChartMeta([]);
    resetForecast();
    setChartState("is-empty", t("chart.sameCurrency"));
    return;
  }

  const requestId = ++appState.activeChartRequestId;
  setChartState("is-loading", t("chart.loadingPair"));

  try {
    const chartDays = appState.chartRangeDays;
    const forecastDays = 365;
    const chartPromise = fetchHistoricalRates(fromCurrency, toCurrency, chartDays);
    const forecastPromise = chartDays === forecastDays
      ? chartPromise
      : fetchHistoricalRates(fromCurrency, toCurrency, forecastDays);
    const [chartResult, forecastResult] = await Promise.allSettled([chartPromise, forecastPromise]);

    if (requestId !== appState.activeChartRequestId) {
      return;
    }

    if (chartResult.status !== "fulfilled") {
      throw chartResult.reason;
    }

    appState.currentChartPoints = chartResult.value;
    renderHistoryChart(chartResult.value);

    if (forecastResult.status === "fulfilled") {
      appState.currentForecastPoints = forecastResult.value;
      updateForecast(forecastResult.value);
    } else {
      appState.currentForecastPoints = [];
      resetForecast();
      forecastSummary.textContent = t("errors.longHistoryUnavailable");
    }
  } catch (error) {
    if (requestId !== appState.activeChartRequestId) {
      return;
    }

    appState.currentChartPoints = [];
    appState.currentForecastPoints = [];
    historyChart.innerHTML = "";
    updateChartMeta([]);
    resetForecast();
    setChartState("is-error", error.message || t("errors.chartUnavailable"));
  }
}

async function recalculate() {
  const rawAmount = amountInput.value.trim();
  const amount = sanitizeAmount(amountInput.value);
  const fromCurrency = fromCurrencySelect.value;
  const toCurrency = toCurrencySelect.value;

  if (!fromCurrency || !toCurrency) {
    return;
  }

  if (amount === null) {
    if (rawAmount) {
      renderInvalidAmountState();
      return;
    }

    renderIdleState();
    return;
  }

  if (fromCurrency === toCurrency) {
    appState.latestRatePayload = null;
    setLoadingSkeleton(false);
    resultValue.textContent = `${formatters.result.format(amount)} ${toCurrency}`;
    resultHint.textContent = t("status.sameCurrencyHint");
    rateLine.textContent = `1 ${fromCurrency} = 1 ${toCurrency}`;
    updatedLine.textContent = t("status.sameCurrencyUpdated", {
      updatedAt: formatters.timestamp.format(new Date())
    });
    setResultState("is-success", t("status.noRate"));
    setStatusState("is-neutral", t("status.sameCurrencyStatus"));
    liveBadge.textContent = t("status.sameCurrencyBadge");
    return;
  }

  const requestId = ++appState.activeRequestId;
  renderLoadingState();

  try {
    const payload = await fetchRate(fromCurrency, toCurrency);
    if (requestId !== appState.activeRequestId) {
      return;
    }

    renderSuccessState(payload, amount, fromCurrency, toCurrency);
  } catch (error) {
    if (requestId !== appState.activeRequestId) {
      return;
    }

    renderErrorState(error.message || t("errors.rateUnavailable"));
  }
}

function swapCurrencies() {
  triggerSwapAnimation();
  const previousFrom = fromCurrencySelect.value;
  fromCurrencySelect.value = toCurrencySelect.value;
  toCurrencySelect.value = previousFrom;
  updatePickerTrigger(fromCurrencySelect);
  updatePickerTrigger(toCurrencySelect);
  recalculate();
  updateHistoricalChart();
}

async function init() {
  loadStoredLanguage();
  updateLocaleFormatters();
  applyStaticTranslations();
  syncLanguageButtons();
  updatePickerTrigger(fromCurrencySelect);
  updatePickerTrigger(toCurrencySelect);
  chartSubtitle.textContent = t("chart.defaultSubtitle");
  resetForecast();
  setChartState("is-loading", t("chart.loading"));
  renderLoadingState();
  loadStoredForecastMode();
  syncForecastModeButtons();

  try {
    const currencies = await fetchCurrencies();
    appState.currencies = currencies;
    appState.currencyMap = new Map(currencies.map((currency) => [currency.code, currency]));

    const fallbackTo = appState.currencyMap.has(DEFAULT_TO) ? DEFAULT_TO : "EUR";
    fillCurrencySelect(fromCurrencySelect, DEFAULT_FROM);
    fillCurrencySelect(toCurrencySelect, fallbackTo);
    updatePickerTrigger(fromCurrencySelect);
    updatePickerTrigger(toCurrencySelect);

    setLoadingSkeleton(false);
    setStatusState("is-live", t("status.currenciesLoaded"));
    liveBadge.textContent = t("status.apiReady");

    await recalculate();
    await updateHistoricalChart();
  } catch (error) {
    setLoadingSkeleton(false);
    setResultState("is-error", t("status.errorState"));
    resultValue.textContent = t("status.noConnectionValue");
    resultHint.textContent = t("status.noConnectionHint");
    rateLine.textContent = t("status.noConnectionRate");
    updatedLine.textContent = t("status.noConnectionUpdated");
    setStatusState("is-error", error.message || t("errors.connectApi"));
    liveBadge.textContent = t("status.noApiBadge");
    appState.currentChartPoints = [];
    appState.currentForecastPoints = [];
    historyChart.innerHTML = "";
    updateChartMeta([]);
    resetForecast();
    setChartState("is-error", error.message || t("errors.loadHistorical"));
  }
}

amountInput.addEventListener("input", recalculate);
chartRangeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const nextRange = Number(button.dataset.range);
    if (!Number.isFinite(nextRange) || nextRange === appState.chartRangeDays) {
      return;
    }

    appState.chartRangeDays = nextRange;
    chartRangeButtons.forEach((item) => {
      const isActive = item === button;
      item.classList.toggle("is-active", isActive);
      item.setAttribute("aria-pressed", String(isActive));
    });
    updateHistoricalChart();
  });
});
forecastModeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const nextMode = button.dataset.forecastMode;
    if (!nextMode || nextMode === appState.forecastMode) {
      return;
    }

    appState.forecastMode = nextMode;
    persistForecastMode();
    syncForecastModeButtons();
    updateHistoricalChart();
  });
});
languageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setLanguage(button.dataset.language);
  });
});
copyForecastButton.addEventListener("click", async () => {
  const summary = [
    t("forecast.summaryHeading"),
    "",
    t("forecast.summaryScenario", { value: forecastDirection.textContent }),
    t("forecast.summarySpot", { value: forecastSpot.textContent }),
    t("forecast.summaryTomorrow", { value: `${forecastTomorrow.textContent.replace(/\s+/g, " ").trim()} | ${forecastTomorrowDelta.textContent}` }),
    t("forecast.summaryWeek", { value: `${forecastWeek.textContent.replace(/\s+/g, " ").trim()} | ${forecastWeekDelta.textContent}` }),
    t("forecast.summaryMonth", { value: `${forecastMonth.textContent.replace(/\s+/g, " ").trim()} | ${forecastMonthDelta.textContent}` }),
    "",
    t("forecast.summaryParamsHeading"),
    t("forecast.summaryConfidence", { value: forecastConfidence.textContent }),
    t("forecast.summarySignal", { value: forecastSignalStrength.textContent }),
    t("forecast.summaryVolatility", { value: forecastVolatility.textContent }),
    t("forecast.summaryMode", { value: forecastMode.textContent }),
    "",
    t("forecast.summaryInterpretationHeading"),
    `- ${forecastReason.textContent}`,
    `- ${forecastInsight.textContent}`,
    "",
    `> ${forecastDisclaimer.textContent}`
  ].join("\n");

  try {
    await navigator.clipboard.writeText(summary);
    copyForecastButton.textContent = t("forecast.copied");
    window.setTimeout(() => {
      copyForecastButton.textContent = t("forecast.copy");
    }, 1400);
  } catch (error) {
    copyForecastButton.textContent = t("forecast.copyFailed");
    window.setTimeout(() => {
      copyForecastButton.textContent = t("forecast.copy");
    }, 1400);
  }
});
swapButton.addEventListener("click", swapCurrencies);
swapButton.addEventListener("animationend", () => {
  swapButton.classList.remove("is-swapping");
});

currencyPickers.forEach((pickerElement) => {
  const selectElement = pickerElement.querySelector("select");
  setupPicker(selectElement);
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".currency-picker")) {
    closeAllPickers();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeAllPickers();
  }
});

init();

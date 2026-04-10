const state = {
  authMode: "login",
  bootPending: true,
  bootError: "",
  currentUser: null,
  chats: [],
  directoryUsers: [],
  messagesByChat: {},
  activeChatId: null,
  eventSource: null,
  authPending: false,
  composerPending: false,
  chatCreatorOpen: false,
  chatCreatorPending: false,
  chatCreatorError: "",
  appStatus: "idle",
  appError: "",
  realtimeWanted: false,
  realtimeReconnectTimer: null,
  realtimeReconnectAttempt: 0,
  realtimeConnectionId: 0,
  renderedChatId: null,
  messageScrollPinned: true,
  forceMessageScroll: false,
};

const AUTH_PATH = "/";
const APP_PATH = "/app";
const USERNAME_RE = /^[a-zA-Z0-9_]{3,20}$/;
const DISPLAY_NAME_MIN_LENGTH = 2;
const DISPLAY_NAME_MAX_LENGTH = 30;
const PASSWORD_MIN_LENGTH = 8;
const PASSWORD_MAX_LENGTH = 64;
const MESSAGE_MAX_LENGTH = 500;
const REALTIME_RECONNECT_BASE_DELAY_MS = 1_000;
const REALTIME_RECONNECT_MAX_DELAY_MS = 5_000;
const MOBILE_LAYOUT_BREAKPOINT_PX = 980;

const timeFormatter = new Intl.DateTimeFormat("ru-RU", {
  hour: "2-digit",
  minute: "2-digit",
});

const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "short",
});

const fullDateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

const elements = {};
let appInitialized = false;

initializeApp();

function initializeApp() {
  if (appInitialized) {
    return;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeApp, { once: true });
    return;
  }

  appInitialized = true;
  cacheElements();
  bindEvents();
  render();
  bootstrap();
}

function cacheElements() {
  elements.bootView = document.getElementById("bootView");
  elements.bootLoader = document.getElementById("bootLoader");
  elements.bootTitle = document.getElementById("bootTitle");
  elements.bootMessage = document.getElementById("bootMessage");
  elements.bootRetryButton = document.getElementById("bootRetryButton");
  elements.authView = document.getElementById("authView");
  elements.appView = document.getElementById("appView");
  elements.toggleLogin = document.getElementById("toggleLogin");
  elements.toggleRegister = document.getElementById("toggleRegister");
  elements.loginForm = document.getElementById("loginForm");
  elements.registerForm = document.getElementById("registerForm");
  elements.loginSubmitButton = elements.loginForm.querySelector('button[type="submit"]');
  elements.registerSubmitButton = elements.registerForm.querySelector('button[type="submit"]');
  elements.authCopy = document.getElementById("authCopy");
  elements.authError = document.getElementById("authError");
  elements.chatList = document.getElementById("chatList");
  elements.chatCount = document.getElementById("chatCount");
  elements.currentUserName = document.getElementById("currentUserName");
  elements.currentUserHandle = document.getElementById("currentUserHandle");
  elements.connectionStatus = document.getElementById("connectionStatus");
  elements.newChatToggleButton = document.getElementById("newChatToggleButton");
  elements.newChatCloseButton = document.getElementById("newChatCloseButton");
  elements.newChatPanel = document.getElementById("newChatPanel");
  elements.newChatList = document.getElementById("newChatList");
  elements.newChatError = document.getElementById("newChatError");
  elements.reloadAppButton = document.getElementById("reloadAppButton");
  elements.logoutButton = document.getElementById("logoutButton");
  elements.panelState = document.getElementById("panelState");
  elements.chatBody = document.getElementById("chatBody");
  elements.chatTitle = document.getElementById("chatTitle");
  elements.chatMeta = document.getElementById("chatMeta");
  elements.chatLastActivity = document.getElementById("chatLastActivity");
  elements.chatBackButton = document.getElementById("chatBackButton");
  elements.messageList = document.getElementById("messageList");
  elements.composerForm = document.getElementById("composerForm");
  elements.messageInput = document.getElementById("messageInput");
  elements.sendButton = document.getElementById("sendButton");
  elements.composerError = document.getElementById("composerError");
}

function bindEvents() {
  elements.bootRetryButton.addEventListener("click", bootstrap);
  elements.toggleLogin.addEventListener("click", () => setAuthMode("login"));
  elements.toggleRegister.addEventListener("click", () => setAuthMode("register"));
  elements.loginForm.addEventListener("submit", handleLogin);
  elements.registerForm.addEventListener("submit", handleRegister);
  elements.chatList.addEventListener("click", handleChatListClick);
  elements.panelState.addEventListener("click", handlePanelStateClick);
  elements.newChatToggleButton.addEventListener("click", handleNewChatToggle);
  elements.newChatCloseButton.addEventListener("click", handleNewChatClose);
  elements.newChatList.addEventListener("click", handleNewChatListClick);
  elements.composerForm.addEventListener("submit", handleSendMessage);
  elements.messageInput.addEventListener("input", handleComposerInput);
  elements.messageInput.addEventListener("keydown", handleComposerKeydown);
  elements.messageList.addEventListener("scroll", handleMessageListScroll);
  elements.reloadAppButton.addEventListener("click", () => loadAppData({ preserveSelection: true }));
  elements.logoutButton.addEventListener("click", handleLogout);
  elements.chatBackButton.addEventListener("click", handleChatBack);
  window.addEventListener("beforeunload", disconnectRealtime);
  window.addEventListener("online", handleWindowOnline);
  window.addEventListener("offline", handleWindowOffline);
  window.addEventListener("popstate", syncRouteWithSession);
  window.addEventListener("resize", handleWindowResize);
}

function render() {
  const showBoot = state.bootPending || Boolean(state.bootError);
  const authenticated = Boolean(state.currentUser);

  elements.bootView.classList.toggle("hidden", !showBoot);
  elements.authView.classList.toggle("hidden", showBoot || authenticated);
  elements.appView.classList.toggle("hidden", showBoot || !authenticated);

  if (showBoot) {
    renderBootState();
    return;
  }

  renderAuthMode();

  if (!authenticated) {
    return;
  }

  renderMessenger();
}

function renderBootState() {
  const hasError = Boolean(state.bootError);
  elements.bootLoader.classList.toggle("hidden", hasError);
  elements.bootRetryButton.classList.toggle("hidden", !hasError);
  elements.bootTitle.textContent = hasError
    ? "Не удалось открыть мессенджер"
    : "Загружаем мессенджер";
  elements.bootMessage.textContent = hasError
    ? state.bootError
    : "Проверяем сессию и подготавливаем список чатов.";
}

function renderAuthMode() {
  const loginActive = state.authMode === "login";
  elements.toggleLogin.classList.toggle("is-active", loginActive);
  elements.toggleRegister.classList.toggle("is-active", !loginActive);
  elements.loginForm.classList.toggle("hidden", !loginActive);
  elements.registerForm.classList.toggle("hidden", loginActive);
  elements.authCopy.textContent = loginActive
    ? "Войдите, чтобы открыть приватную часть мессенджера."
    : "Создайте аккаунт и вы сразу попадете в приватный раздел.";
}

function renderMessenger() {
  const mobileChatOpen = shouldUseMobileChatView();

  elements.currentUserName.textContent = state.currentUser.displayName;
  elements.currentUserHandle.textContent = `@${state.currentUser.username}`;
  elements.chatCount.textContent = String(state.chats.length);
  elements.appView.classList.toggle("is-mobile-layout", isMobileLayout());
  elements.appView.classList.toggle("is-chat-open", mobileChatOpen);
  elements.chatBackButton.classList.toggle("hidden", !mobileChatOpen);
  elements.newChatToggleButton.textContent = state.chatCreatorPending
    ? "Открываем..."
    : state.chatCreatorOpen
      ? "Скрыть"
      : "Новый диалог";
  elements.newChatToggleButton.disabled = state.appStatus === "loading" || state.chatCreatorPending;
  elements.newChatToggleButton.setAttribute("aria-expanded", String(state.chatCreatorOpen));
  elements.newChatCloseButton.disabled = state.chatCreatorPending;
  elements.newChatCloseButton.textContent = state.chatCreatorPending ? "Подождите..." : "Закрыть";
  elements.reloadAppButton.disabled = state.appStatus === "loading";
  elements.reloadAppButton.textContent = state.appStatus === "loading" ? "Обновляем..." : "Обновить";
  elements.chatList.setAttribute("aria-busy", String(state.appStatus === "loading"));
  elements.newChatList.setAttribute("aria-busy", String(state.chatCreatorPending));

  renderNewChatPanel();
  renderChatList();
  renderChatPanel();
}

function renderNewChatPanel() {
  elements.newChatPanel.classList.toggle("hidden", !state.chatCreatorOpen);
  elements.newChatPanel.classList.toggle("is-busy", state.chatCreatorPending);
  elements.newChatError.textContent = state.chatCreatorError;

  if (!state.chatCreatorOpen) {
    elements.newChatList.innerHTML = "";
    return;
  }

  if (state.appStatus === "loading") {
    elements.newChatList.innerHTML = renderDirectorySkeletons();
    return;
  }

  if (!state.directoryUsers.length) {
    elements.newChatList.innerHTML = renderStateCard({
      eyebrow: "Empty",
      title: "Пока некого добавить",
      description: "Как только в системе появятся другие пользователи, здесь можно будет открыть личный чат.",
    });
    return;
  }

  elements.newChatList.innerHTML = state.directoryUsers.map(renderDirectoryUserCard).join("");
}

function renderChatList() {
  if (state.appStatus === "loading") {
    elements.chatList.innerHTML = renderChatListSkeletons();
    return;
  }

  if (state.appStatus === "error") {
    elements.chatList.innerHTML = renderStateCard({
      eyebrow: "Load error",
      title: "Не удалось загрузить чаты",
      description: state.appError || "Попробуйте обновить данные еще раз.",
      action: "retry-app",
      actionLabel: "Повторить",
    });
    return;
  }

  if (!state.chats.length) {
    elements.chatList.innerHTML = renderStateCard({
      eyebrow: "Empty",
      title: "Чатов пока нет",
      description: "Откройте «Новый диалог» и выберите пользователя, чтобы начать переписку.",
    });
    return;
  }

  elements.chatList.innerHTML = state.chats.map(renderChatCard).join("");
}

function renderChatPanel() {
  if (state.appStatus === "loading") {
    showPanelState(renderPanelLoading());
    return;
  }

  if (state.appStatus === "error") {
    showPanelState(
      renderStateCard({
        eyebrow: "Load error",
        title: "Не удалось загрузить активный чат",
        description: state.appError || "Обновите данные и попробуйте еще раз.",
        action: "retry-app",
        actionLabel: "Обновить",
      }),
    );
    return;
  }

  const activeChat = getActiveChat();
  if (!activeChat) {
    state.renderedChatId = null;
    state.messageScrollPinned = true;
    state.forceMessageScroll = false;
    showPanelState(
      renderStateCard({
        eyebrow: "No chat selected",
        title: "Выберите диалог слева",
        description: "Справа появятся история переписки, статус собеседника и поле для отправки сообщений.",
      }),
    );
    return;
  }

  const scrollSnapshot = getMessageListSnapshot(activeChat.id);
  hidePanelState();
  elements.chatTitle.textContent = activeChat.peer.displayName;
  elements.chatMeta.textContent = getPresenceLabel(activeChat.peer, { compact: false });
  elements.chatLastActivity.textContent = activeChat.lastMessage
    ? `Последнее сообщение ${formatFullStamp(activeChat.lastMessage.createdAt)}`
    : "Сообщений пока нет";

  const messages = state.messagesByChat[activeChat.id] || [];
  if (!messages.length) {
    elements.messageList.innerHTML = `
      <div class="message-list__empty">
        <p class="eyebrow">Empty conversation</p>
        <h3>История пока пустая</h3>
        <p>Отправьте первое сообщение, чтобы начать переписку.</p>
      </div>
    `;
  } else {
    elements.messageList.innerHTML = messages.map((message) => renderMessage(message)).join("");
  }

  elements.messageInput.disabled = state.composerPending;
  elements.sendButton.disabled = state.composerPending;
  elements.sendButton.textContent = state.composerPending ? "Отправка..." : "Отправить";
  elements.messageInput.placeholder = state.composerPending
    ? "Отправляем сообщение..."
    : `Сообщение для ${activeChat.peer.displayName}`;
  elements.messageList.setAttribute("aria-busy", String(state.composerPending));
  syncMessageListAfterRender(activeChat.id, scrollSnapshot);
}

async function bootstrap() {
  state.bootPending = true;
  state.bootError = "";
  render();

  try {
    const payload = await request("/api/bootstrap", { resetOnUnauthorized: false });
    applySession(payload, { preserveSelection: false });
  } catch (error) {
    if (error.status === 401) {
      state.bootPending = false;
      resetSession();
      return;
    }

    state.bootPending = false;
    state.bootError = error.message || "Не удалось загрузить приложение.";
    render();
  }
}

async function loadAppData({ preserveSelection } = { preserveSelection: true }) {
  if (!state.currentUser) {
    return;
  }

  state.appStatus = "loading";
  state.appError = "";
  render();

  try {
    const payload = await request("/api/bootstrap", { resetOnUnauthorized: false });
    applySession(payload, { preserveSelection });
  } catch (error) {
    if (error.status === 401) {
      resetSession("Сессия истекла. Выполните вход заново.");
      return;
    }

    state.appStatus = "error";
    state.appError = error.message || "Не удалось загрузить список чатов.";
    render();
  }
}

async function handleLogin(event) {
  event.preventDefault();
  const formData = new FormData(elements.loginForm);
  const username = normalizeUsername(formData.get("username"));
  const password = String(formData.get("password") || "");

  const validationError = validateLoginForm({ username, password });
  if (validationError) {
    elements.authError.textContent = validationError;
    return;
  }

  try {
    setAuthPending(true);
    elements.authError.textContent = "";
    const payload = await request("/api/auth/login", {
      method: "POST",
      body: { username, password },
      resetOnUnauthorized: false,
    });
    applySession(payload, { preserveSelection: false });
  } catch (error) {
    elements.authError.textContent = error.message;
  } finally {
    setAuthPending(false);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const formData = new FormData(elements.registerForm);
  const displayName = String(formData.get("displayName") || "").trim();
  const username = normalizeUsername(formData.get("username"));
  const password = String(formData.get("password") || "");

  const validationError = validateRegisterForm({ displayName, username, password });
  if (validationError) {
    elements.authError.textContent = validationError;
    return;
  }

  try {
    setAuthPending(true);
    elements.authError.textContent = "";
    const payload = await request("/api/auth/register", {
      method: "POST",
      body: { displayName, username, password },
      resetOnUnauthorized: false,
    });
    applySession(payload, { preserveSelection: false });
  } catch (error) {
    elements.authError.textContent = error.message;
  } finally {
    setAuthPending(false);
  }
}

async function handleSendMessage(event) {
  event.preventDefault();

  if (!state.activeChatId || state.composerPending) {
    return;
  }

  const text = elements.messageInput.value;
  const validationError = validateMessageText(text);
  if (validationError) {
    elements.composerError.textContent = validationError;
    return;
  }

  let sentSuccessfully = false;

  try {
    setComposerPending(true);
    elements.composerError.textContent = "";
    const payload = await request("/api/messages", {
      method: "POST",
      body: { chatId: state.activeChatId, text: text.trim() },
    });
    mergeMessageEvent(payload, { forceScroll: true });
    resetComposer();
    sentSuccessfully = true;
  } catch (error) {
    elements.composerError.textContent = error.message;
  } finally {
    setComposerPending(false);
    if (sentSuccessfully) {
      focusComposer();
    }
  }
}

async function handleLogout() {
  disconnectRealtime();

  try {
    await request("/api/auth/logout", {
      method: "POST",
      resetOnUnauthorized: false,
    });
  } catch (error) {
    console.error(error);
  }

  resetSession();
}

function handleNewChatToggle() {
  state.chatCreatorOpen = !state.chatCreatorOpen;
  state.chatCreatorError = "";
  render();
}

function handleNewChatClose() {
  state.chatCreatorOpen = false;
  state.chatCreatorError = "";
  render();
}

function handleChatBack() {
  if (!shouldUseMobileChatView()) {
    return;
  }

  if (isChatHistoryState(window.history.state)) {
    window.history.back();
    return;
  }

  closeActiveChat({ syncHistory: true });
}

async function handleNewChatListClick(event) {
  const button = event.target.closest("[data-peer-id]");
  if (!button || state.chatCreatorPending) {
    return;
  }

  const peerId = String(button.dataset.peerId || "");
  if (!peerId) {
    return;
  }

  let focusAfterOpen = false;
  state.chatCreatorPending = true;
  state.chatCreatorError = "";
  render();

  try {
    const payload = await request("/api/chats/direct", {
      method: "POST",
      body: { peerId },
    });
    applyDirectChatPayload(payload);
    focusAfterOpen = true;
  } catch (error) {
    state.chatCreatorError = error.message;
  } finally {
    state.chatCreatorPending = false;
    render();
    if (focusAfterOpen) {
      focusComposer();
    }
  }
}

function handleChatListClick(event) {
  const actionButton = event.target.closest("[data-action]");
  if (actionButton) {
    handleAction(actionButton.dataset.action);
    return;
  }

  const button = event.target.closest("[data-chat-id]");
  if (!button) {
    return;
  }

  openChat(button.dataset.chatId);
}

function handlePanelStateClick(event) {
  const actionButton = event.target.closest("[data-action]");
  if (!actionButton) {
    return;
  }
  handleAction(actionButton.dataset.action);
}

function handleAction(action) {
  if (action === "retry-app") {
    if (state.currentUser) {
      loadAppData({ preserveSelection: true });
      return;
    }
    bootstrap();
  }
}

function handleComposerInput() {
  elements.composerError.textContent = "";
  autoResizeComposer();
}

function handleMessageListScroll() {
  if (state.renderedChatId !== state.activeChatId) {
    return;
  }

  state.messageScrollPinned = isMessageListNearBottom();
}

function handleComposerKeydown(event) {
  if (event.key !== "Enter" || event.shiftKey || event.isComposing) {
    return;
  }

  event.preventDefault();

  if (!state.activeChatId || state.composerPending) {
    return;
  }

  elements.composerForm.requestSubmit();
}

function handleWindowResize() {
  if (!state.currentUser) {
    return;
  }

  if (isMobileLayout() && state.activeChatId && !isChatHistoryState(window.history.state)) {
    navigateTo(APP_PATH, getAppChatHistoryState(state.activeChatId), { replace: true });
  }

  render();
}

function applySession(payload, { preserveSelection } = { preserveSelection: true }) {
  const sameUser = state.currentUser?.id === payload.currentUser?.id;
  const nextChats = sameUser
    ? mergeChatCollections(state.chats, payload.chats || [])
    : sortChats(payload.chats || []);
  const nextMessagesByChat = sameUser
    ? mergeMessagesByChat(state.messagesByChat, payload.messagesByChat || {})
    : normalizeMessagesByChat(payload.messagesByChat || {});
  const keepActiveChat =
    preserveSelection && nextChats.some((chat) => chat.id === state.activeChatId);
  const restoredActiveChatId = getHistoryChatId(nextChats);

  state.bootPending = false;
  state.bootError = "";
  state.currentUser = payload.currentUser;
  state.chats = nextChats;
  state.directoryUsers = sortDirectoryUsers(payload.users || []);
  state.messagesByChat = nextMessagesByChat;
  state.activeChatId = restoredActiveChatId || (keepActiveChat ? state.activeChatId : null);
  state.chatCreatorOpen = sameUser ? state.chatCreatorOpen : false;
  state.chatCreatorPending = false;
  state.chatCreatorError = "";
  state.forceMessageScroll = !(restoredActiveChatId || keepActiveChat);
  state.messageScrollPinned = !(restoredActiveChatId || keepActiveChat) || state.messageScrollPinned;
  state.appStatus = "ready";
  state.appError = "";
  elements.loginForm.reset();
  elements.registerForm.reset();
  elements.authError.textContent = "";
  elements.composerError.textContent = "";
  resetComposer();
  navigateTo(APP_PATH, getAppHistoryState(), { replace: true });
  render();
  connectRealtime();
}

function connectRealtime() {
  if (!state.currentUser) {
    return;
  }

  state.realtimeWanted = true;
  state.realtimeReconnectAttempt = 0;
  clearRealtimeReconnectTimer();

  if (state.eventSource) {
    return;
  }

  if (navigator.onLine === false) {
    setConnectionState("offline");
    scheduleRealtimeReconnect();
    return;
  }

  openRealtimeConnection();
}

function disconnectRealtime() {
  state.realtimeWanted = false;
  state.realtimeReconnectAttempt = 0;
  state.realtimeConnectionId += 1;
  clearRealtimeReconnectTimer();
  closeRealtimeSource();
  setConnectionState("offline");
}

function openRealtimeConnection() {
  if (!state.realtimeWanted || !state.currentUser || state.eventSource) {
    return;
  }

  const connectionId = state.realtimeConnectionId + 1;
  state.realtimeConnectionId = connectionId;

  const source = new EventSource("/api/events");
  state.eventSource = source;

  source.addEventListener("open", () => {
    if (!isCurrentRealtimeConnection(source, connectionId)) {
      source.close();
      return;
    }

    state.realtimeReconnectAttempt = 0;
    clearRealtimeReconnectTimer();
    setConnectionState("online");
  });

  source.addEventListener("app-event", (event) => {
    if (!isCurrentRealtimeConnection(source, connectionId)) {
      return;
    }

    handleRealtimePacket(event.data);
  });

  source.addEventListener("error", () => {
    if (!isCurrentRealtimeConnection(source, connectionId)) {
      return;
    }

    closeRealtimeSource(source);

    if (!state.realtimeWanted || !state.currentUser) {
      setConnectionState("offline");
      return;
    }

    setConnectionState(navigator.onLine === false ? "offline" : "reconnecting");
    scheduleRealtimeReconnect();
  });
}

function handleRealtimePacket(rawPacket) {
  let packet;

  try {
    packet = JSON.parse(rawPacket);
  } catch (error) {
    console.error("Failed to parse realtime event.", error);
    return;
  }

  if (packet.type === "stream.ready") {
    setConnectionState("online");
    return;
  }

  if (packet.type === "message.created") {
    mergeMessageEvent(packet.payload);
    return;
  }

  if (packet.type === "presence.updated") {
    applyPresenceEvent(packet.payload);
  }
}

function scheduleRealtimeReconnect() {
  if (
    !state.realtimeWanted ||
    !state.currentUser ||
    state.eventSource ||
    state.realtimeReconnectTimer
  ) {
    return;
  }

  const delay = Math.min(
    REALTIME_RECONNECT_BASE_DELAY_MS * (2 ** state.realtimeReconnectAttempt),
    REALTIME_RECONNECT_MAX_DELAY_MS,
  );
  state.realtimeReconnectAttempt += 1;

  state.realtimeReconnectTimer = window.setTimeout(() => {
    state.realtimeReconnectTimer = null;
    openRealtimeConnection();
  }, delay);
}

function clearRealtimeReconnectTimer() {
  if (!state.realtimeReconnectTimer) {
    return;
  }

  window.clearTimeout(state.realtimeReconnectTimer);
  state.realtimeReconnectTimer = null;
}

function closeRealtimeSource(source = state.eventSource) {
  if (!source) {
    return;
  }

  if (state.eventSource === source) {
    state.eventSource = null;
  }

  source.close();
}

function isCurrentRealtimeConnection(source, connectionId) {
  return (
    state.realtimeWanted &&
    state.eventSource === source &&
    state.realtimeConnectionId === connectionId
  );
}

function handleWindowOnline() {
  if (!state.realtimeWanted || !state.currentUser) {
    return;
  }

  clearRealtimeReconnectTimer();
  setConnectionState("reconnecting");
  openRealtimeConnection();
}

function handleWindowOffline() {
  if (!state.realtimeWanted) {
    return;
  }

  clearRealtimeReconnectTimer();
  closeRealtimeSource();
  setConnectionState("offline");
}

function mergeMessageEvent(payload, { forceScroll = false } = {}) {
  if (!state.currentUser) {
    return;
  }

  upsertChat(payload.chat);
  state.messagesByChat = {
    ...state.messagesByChat,
    [payload.chatId]: mergeMessageLists(
      state.messagesByChat[payload.chatId] || [],
      [payload.message],
    ),
  };
  if (forceScroll && payload.chatId === state.activeChatId) {
    state.forceMessageScroll = true;
  }

  render();
}

function applyDirectChatPayload(payload) {
  upsertChat(payload.chat);
  state.messagesByChat = {
    ...state.messagesByChat,
    [payload.chatId]: mergeMessageLists(
      state.messagesByChat[payload.chatId] || [],
      payload.messages || [],
    ),
  };
  state.chatCreatorOpen = false;
  state.chatCreatorError = "";
  openChat(payload.chatId, { focusComposerAfter: false, forceScroll: true });
}

function applyPresenceEvent(payload) {
  let changed = false;

  state.chats = state.chats.map((chat) => {
    if (chat.peer.id !== payload.userId) {
      return chat;
    }

    if (chat.peer.online === payload.online && chat.peer.lastSeenAt === payload.lastSeenAt) {
      return chat;
    }

    changed = true;
    return {
      ...chat,
      peer: {
        ...chat.peer,
        online: payload.online,
        lastSeenAt: payload.lastSeenAt || chat.peer.lastSeenAt || null,
      },
    };
  });

  state.directoryUsers = state.directoryUsers.map((user) => {
    if (user.id !== payload.userId) {
      return user;
    }

    if (user.online === payload.online && user.lastSeenAt === payload.lastSeenAt) {
      return user;
    }

    changed = true;
    return {
      ...user,
      online: payload.online,
      lastSeenAt: payload.lastSeenAt || user.lastSeenAt || null,
    };
  });

  if (changed) {
    render();
  }
}

function upsertChat(nextChat) {
  const existingIndex = state.chats.findIndex((chat) => chat.id === nextChat.id);

  if (existingIndex === -1) {
    state.chats = sortChats([nextChat, ...state.chats]);
    return;
  }

  state.chats[existingIndex] = mergeChatRecord(state.chats[existingIndex], nextChat);
  state.chats = sortChats([...state.chats]);
}

function mergeChatCollections(currentChats, incomingChats) {
  const chatsById = new Map(currentChats.map((chat) => [chat.id, chat]));

  for (const incomingChat of incomingChats) {
    const currentChat = chatsById.get(incomingChat.id);
    chatsById.set(
      incomingChat.id,
      currentChat ? mergeChatRecord(currentChat, incomingChat) : incomingChat,
    );
  }

  return sortChats([...chatsById.values()]);
}

function mergeChatRecord(currentChat, incomingChat) {
  if (!currentChat) {
    return incomingChat;
  }

  if (!incomingChat) {
    return currentChat;
  }

  const currentStamp = getChatActivityTimestamp(currentChat);
  const incomingStamp = getChatActivityTimestamp(incomingChat);
  const preferredChat = incomingStamp >= currentStamp ? incomingChat : currentChat;
  const mergedPeer = currentChat.peer.id === incomingChat.peer.id
    ? mergePeerPresence(currentChat.peer, preferredChat.peer)
    : preferredChat.peer;

  return {
    ...preferredChat,
    peer: mergedPeer,
  };
}

function mergePeerPresence(currentPeer, incomingPeer) {
  if (!currentPeer) {
    return incomingPeer;
  }

  if (!incomingPeer) {
    return currentPeer;
  }

  const currentLastSeenAt = getPresenceTimestamp(currentPeer.lastSeenAt);
  const incomingLastSeenAt = getPresenceTimestamp(incomingPeer.lastSeenAt);

  return {
    ...incomingPeer,
    online: Boolean(incomingPeer.online),
    lastSeenAt: currentLastSeenAt >= incomingLastSeenAt
      ? currentPeer.lastSeenAt || incomingPeer.lastSeenAt || null
      : incomingPeer.lastSeenAt || currentPeer.lastSeenAt || null,
  };
}

function getPresenceTimestamp(value) {
  if (!value) {
    return 0;
  }

  const timestamp = new Date(value).getTime();
  return Number.isFinite(timestamp) ? timestamp : 0;
}

function getChatActivityTimestamp(chat) {
  return new Date(chat.lastMessage?.createdAt || chat.updatedAt).getTime();
}

function normalizeMessagesByChat(messagesByChat) {
  const normalized = {};

  for (const [chatId, messages] of Object.entries(messagesByChat)) {
    normalized[chatId] = mergeMessageLists([], messages);
  }

  return normalized;
}

function mergeMessagesByChat(currentMessagesByChat, incomingMessagesByChat) {
  const merged = { ...currentMessagesByChat };

  for (const [chatId, incomingMessages] of Object.entries(incomingMessagesByChat)) {
    merged[chatId] = mergeMessageLists(merged[chatId] || [], incomingMessages);
  }

  return merged;
}

function mergeMessageLists(currentMessages, incomingMessages) {
  const messagesById = new Map(currentMessages.map((message) => [message.id, message]));

  for (const incomingMessage of incomingMessages) {
    messagesById.set(incomingMessage.id, incomingMessage);
  }

  return sortMessages([...messagesById.values()]);
}

function sortMessages(messages) {
  return [...messages].sort((left, right) => {
    const timeDiff =
      new Date(left.createdAt).getTime() - new Date(right.createdAt).getTime();

    if (timeDiff !== 0) {
      return timeDiff;
    }

    return left.id.localeCompare(right.id);
  });
}

async function request(url, options = {}) {
  const fetchOptions = {
    method: options.method || "GET",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  };

  if (options.body) {
    fetchOptions.body = JSON.stringify(options.body);
  }

  let response;
  try {
    response = await fetch(url, fetchOptions);
  } catch (error) {
    const networkError = new Error("Сеть недоступна. Проверьте, что сервер запущен.");
    networkError.status = 0;
    throw networkError;
  }

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = new Error(payload.error || "Не удалось выполнить запрос.");
    error.status = response.status;

    if (response.status === 401 && options.resetOnUnauthorized !== false) {
      resetSession(error.message);
    }

    throw error;
  }

  return payload;
}

function getActiveChat() {
  return state.chats.find((chat) => chat.id === state.activeChatId) || null;
}

function getMessageListSnapshot(chatId) {
  const isSameChat = state.renderedChatId === chatId;

  if (!isSameChat) {
    return {
      shouldStick: true,
      scrollTop: 0,
    };
  }

  return {
    shouldStick: state.forceMessageScroll || state.messageScrollPinned || isMessageListNearBottom(),
    scrollTop: elements.messageList.scrollTop,
  };
}

function syncMessageListAfterRender(chatId, snapshot) {
  state.renderedChatId = chatId;

  window.requestAnimationFrame(() => {
    if (state.renderedChatId !== chatId) {
      return;
    }

    if (snapshot.shouldStick) {
      scrollMessageListToBottom();
    } else {
      elements.messageList.scrollTop = snapshot.scrollTop;
    }

    state.messageScrollPinned = isMessageListNearBottom();
    state.forceMessageScroll = false;
  });
}

function scrollMessageListToBottom() {
  elements.messageList.scrollTop = elements.messageList.scrollHeight;
}

function isMessageListNearBottom() {
  const threshold = 40;
  const remaining =
    elements.messageList.scrollHeight -
    elements.messageList.scrollTop -
    elements.messageList.clientHeight;

  return remaining <= threshold;
}

function getDirectChatByPeerId(peerId) {
  return state.chats.find((chat) => chat.peer.id === peerId) || null;
}

function renderChatCard(chat) {
  const activeClass = chat.id === state.activeChatId ? "is-active" : "";
  const preview = getChatPreview(chat);
  const stamp = formatChatStamp(chat.lastMessage?.createdAt || chat.updatedAt);
  const statusLabel = getPresenceLabel(chat.peer, { compact: true });

  return `
    <button
      class="chat-card ${activeClass}"
      type="button"
      data-chat-id="${chat.id}"
      aria-pressed="${chat.id === state.activeChatId}"
    >
      <div class="chat-card__avatar">${getInitials(chat.peer.displayName)}</div>
      <div class="chat-card__content">
        <div class="chat-card__top">
          <strong>${escapeHtml(chat.peer.displayName)}</strong>
          <span>${stamp}</span>
        </div>
        <div class="chat-card__meta">
          <span class="chat-card__presence">
            <span class="status-dot ${chat.peer.online ? "is-online" : ""}"></span>
            <span>${statusLabel}</span>
          </span>
        </div>
        <p class="chat-card__preview">${escapeHtml(preview)}</p>
      </div>
    </button>
  `;
}

function renderDirectoryUserCard(user) {
  const existingChat = getDirectChatByPeerId(user.id);
  const badgeLabel = existingChat ? "Уже есть чат" : "Новый";
  const actionLabel = state.chatCreatorPending
    ? "Подождите..."
    : existingChat
      ? "Открыть чат"
      : "Создать чат";

  return `
    <button
      class="directory-user-card"
      type="button"
      data-peer-id="${user.id}"
      ${state.chatCreatorPending ? "disabled" : ""}
    >
      <div class="directory-user-card__avatar">${getInitials(user.displayName)}</div>
      <div class="directory-user-card__content">
        <div class="directory-user-card__top">
          <strong>${escapeHtml(user.displayName)}</strong>
          <span class="directory-user-card__badge ${existingChat ? "is-existing" : ""}">
            ${badgeLabel}
          </span>
        </div>
        <div class="directory-user-card__meta">
          <span class="chat-card__presence">
            <span class="status-dot ${user.online ? "is-online" : ""}"></span>
            <span>${getPresenceLabel(user, { compact: true })}</span>
          </span>
          <span>@${escapeHtml(user.username)}</span>
        </div>
        <span class="directory-user-card__action">${actionLabel}</span>
      </div>
    </button>
  `;
}

function renderMessage(message) {
  const mine = message.authorId === state.currentUser.id;

  return `
    <article class="message ${mine ? "message--mine" : ""}">
      <div class="message__bubble">
        <p>${escapeHtml(message.text)}</p>
        <span>${formatMessageTime(message.createdAt)}</span>
      </div>
    </article>
  `;
}

function renderStateCard({ eyebrow, title, description, action, actionLabel }) {
  const actionMarkup = action && actionLabel
    ? `<button class="secondary-button secondary-button--compact" type="button" data-action="${action}">${actionLabel}</button>`
    : "";

  return `
    <div class="state-card">
      <p class="eyebrow">${escapeHtml(eyebrow)}</p>
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(description)}</p>
      ${actionMarkup}
    </div>
  `;
}

function renderChatListSkeletons() {
  return Array.from({ length: 4 }, () => `
    <div class="chat-card chat-card--skeleton" aria-hidden="true">
      <div class="chat-card__avatar skeleton-block"></div>
      <div class="chat-card__content">
        <div class="skeleton-line skeleton-line--title"></div>
        <div class="skeleton-line skeleton-line--meta"></div>
        <div class="skeleton-line skeleton-line--body"></div>
      </div>
    </div>
  `).join("");
}

function renderDirectorySkeletons() {
  return Array.from({ length: 3 }, () => `
    <div class="directory-user-card directory-user-card--skeleton" aria-hidden="true">
      <div class="directory-user-card__avatar skeleton-block"></div>
      <div class="directory-user-card__content">
        <div class="skeleton-line skeleton-line--title"></div>
        <div class="skeleton-line skeleton-line--meta"></div>
        <div class="skeleton-line skeleton-line--body short"></div>
      </div>
    </div>
  `).join("");
}

function renderPanelLoading() {
  return `
    <div class="state-card state-card--loading">
      <p class="eyebrow">Loading</p>
      <h3>Загружаем активный чат</h3>
      <p>Подтягиваем список сообщений и текущее состояние диалога.</p>
      <div class="panel-skeleton">
        <div class="skeleton-line skeleton-line--title"></div>
        <div class="skeleton-line skeleton-line--body"></div>
        <div class="skeleton-line skeleton-line--body short"></div>
      </div>
    </div>
  `;
}

function showPanelState(markup) {
  elements.panelState.classList.remove("hidden");
  elements.chatBody.classList.add("hidden");
  elements.panelState.innerHTML = markup;
}

function hidePanelState() {
  elements.panelState.classList.add("hidden");
  elements.chatBody.classList.remove("hidden");
  elements.panelState.innerHTML = "";
}

function getChatPreview(chat) {
  if (!chat.lastMessage) {
    return "Диалог пока пустой";
  }

  const prefix = chat.lastMessage.authorId === state.currentUser.id ? "Вы: " : "";
  return `${prefix}${chat.lastMessage.text}`;
}

function sortChats(chats) {
  return [...chats].sort((left, right) => {
    return new Date(right.updatedAt).getTime() - new Date(left.updatedAt).getTime();
  });
}

function sortDirectoryUsers(users) {
  return [...users].sort((left, right) => {
    return left.displayName.localeCompare(right.displayName, "ru", { sensitivity: "base" });
  });
}

function setConnectionState(status) {
  const connectionLabel = {
    online: "online",
    offline: "offline",
    reconnecting: "reconnecting",
  }[status] || "offline";

  elements.connectionStatus.textContent = `Realtime: ${connectionLabel}`;
  elements.connectionStatus.classList.toggle("is-live", status === "online");
  elements.connectionStatus.classList.toggle("is-reconnecting", status === "reconnecting");
}

function setAuthMode(mode) {
  state.authMode = mode;
  elements.authError.textContent = "";
  renderAuthMode();
}

function setAuthPending(pending) {
  state.authPending = pending;
  elements.loginSubmitButton.textContent = pending ? "Входим..." : "Войти";
  elements.registerSubmitButton.textContent = pending ? "Создаём..." : "Создать аккаунт";

  for (const form of [elements.loginForm, elements.registerForm]) {
    for (const field of Array.from(form.elements)) {
      field.disabled = pending;
    }
  }
}

function setComposerPending(pending) {
  state.composerPending = pending;
  elements.messageInput.disabled = pending;
  elements.sendButton.disabled = pending;
  elements.sendButton.textContent = pending ? "Отправка..." : "Отправить";
  elements.composerForm.classList.toggle("is-busy", pending);
}

function autoResizeComposer() {
  elements.messageInput.style.height = "auto";
  const nextHeight = Math.min(elements.messageInput.scrollHeight, 180);
  elements.messageInput.style.height = `${nextHeight}px`;
}

function resetComposer() {
  elements.messageInput.value = "";
  elements.messageInput.style.height = "";
}

function focusComposer() {
  if (!state.activeChatId || state.composerPending) {
    return;
  }

  window.requestAnimationFrame(() => {
    elements.messageInput.focus();
  });
}

function resetSession(message = "") {
  disconnectRealtime();
  state.bootPending = false;
  state.bootError = "";
  state.currentUser = null;
  state.chats = [];
  state.directoryUsers = [];
  state.messagesByChat = {};
  state.activeChatId = null;
  state.chatCreatorOpen = false;
  state.chatCreatorPending = false;
  state.chatCreatorError = "";
  state.appStatus = "idle";
  state.appError = "";
  state.renderedChatId = null;
  state.messageScrollPinned = true;
  state.forceMessageScroll = false;
  setAuthMode("login");
  setComposerPending(false);
  navigateTo(AUTH_PATH, getAuthHistoryState(), { replace: true });
  render();
  elements.authError.textContent = message;
}

function navigateTo(path, historyState = {}, { replace = true } = {}) {
  if (
    window.location.pathname === path &&
    areHistoryStatesEqual(window.history.state, historyState)
  ) {
    return;
  }

  const method = replace ? "replaceState" : "pushState";
  window.history[method](historyState, "", path);
}

function syncRouteWithSession(event) {
  if (state.currentUser) {
    if (window.location.pathname !== APP_PATH) {
      navigateTo(APP_PATH, getAppHistoryState(), { replace: true });
      return;
    }

    if (!isMobileLayout()) {
      return;
    }

    const nextActiveChatId = getHistoryChatId(state.chats, event?.state ?? window.history.state);
    if (nextActiveChatId === state.activeChatId) {
      return;
    }

    if (nextActiveChatId) {
      state.activeChatId = nextActiveChatId;
      state.renderedChatId = null;
      state.forceMessageScroll = true;
      state.messageScrollPinned = true;
      elements.composerError.textContent = "";
      render();
      return;
    }

    closeActiveChat({ syncHistory: false });
    return;
  }

  if (window.location.pathname !== AUTH_PATH) {
    navigateTo(AUTH_PATH, getAuthHistoryState(), { replace: true });
  }
}

function formatMessageTime(value) {
  return timeFormatter.format(new Date(value));
}

function formatChatStamp(value) {
  const date = new Date(value);
  const sameDay = new Date().toDateString() === date.toDateString();
  return sameDay ? timeFormatter.format(date) : dateFormatter.format(date);
}

function formatFullStamp(value) {
  return fullDateFormatter.format(new Date(value));
}

function formatPresenceTime(value) {
  return timeFormatter.format(new Date(value));
}

function getPresenceLabel(user, { compact }) {
  if (user.online) {
    return "online";
  }

  const lastSeenAt = user.lastSeenAt;
  if (!lastSeenAt) {
    return compact ? "offline" : "Не в сети";
  }

  const date = new Date(lastSeenAt);
  if (Number.isNaN(date.getTime())) {
    return compact ? "offline" : "Не в сети";
  }

  const diffMs = Date.now() - date.getTime();
  if (diffMs < 60_000) {
    return compact ? "недавно" : "Последний раз в сети недавно";
  }

  const today = new Date();
  if (today.toDateString() === date.toDateString()) {
    return compact
      ? "сегодня"
      : `Последний раз в сети сегодня в ${formatPresenceTime(lastSeenAt)}`;
  }

  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (yesterday.toDateString() === date.toDateString()) {
    return compact
      ? "вчера"
      : `Последний раз в сети вчера в ${formatPresenceTime(lastSeenAt)}`;
  }

  return compact
    ? dateFormatter.format(date)
    : `Последний раз в сети ${formatFullStamp(lastSeenAt)}`;
}

function getInitials(name) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((chunk) => chunk[0]?.toUpperCase() || "")
    .join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function validateLoginForm({ username, password }) {
  if (!username) {
    return "Введите логин.";
  }

  if (!USERNAME_RE.test(username)) {
    return "Логин должен быть 3-20 символов и состоять из букв, цифр или _.";
  }

  if (!password) {
    return "Введите пароль.";
  }

  return "";
}

function validateRegisterForm({ displayName, username, password }) {
  if (displayName.length < DISPLAY_NAME_MIN_LENGTH || displayName.length > DISPLAY_NAME_MAX_LENGTH) {
    return `Имя должно быть длиной от ${DISPLAY_NAME_MIN_LENGTH} до ${DISPLAY_NAME_MAX_LENGTH} символов.`;
  }

  if (!USERNAME_RE.test(username)) {
    return "Логин должен быть 3-20 символов и состоять из букв, цифр или _.";
  }

  if (password !== password.trim()) {
    return "Пароль не должен начинаться или заканчиваться пробелом.";
  }

  if (password.length < PASSWORD_MIN_LENGTH || password.length > PASSWORD_MAX_LENGTH) {
    return `Пароль должен быть длиной от ${PASSWORD_MIN_LENGTH} до ${PASSWORD_MAX_LENGTH} символов.`;
  }

  return "";
}

function validateMessageText(value) {
  const normalizedText = String(value || "").trim();

  if (!normalizedText) {
    return "Введите текст сообщения.";
  }

  if (normalizedText.length > MESSAGE_MAX_LENGTH) {
    return `Сообщение не должно быть длиннее ${MESSAGE_MAX_LENGTH} символов.`;
  }

  return "";
}

function normalizeUsername(value) {
  return String(value || "").trim().toLowerCase();
}

function openChat(chatId, { focusComposerAfter = true, forceScroll = false } = {}) {
  const nextChatId = String(chatId || "");
  if (!nextChatId) {
    return;
  }

  const previousChatId = state.activeChatId;
  const shouldPushHistory = isMobileLayout() && !isChatHistoryState(window.history.state);

  state.activeChatId = nextChatId;
  state.forceMessageScroll = forceScroll || previousChatId !== nextChatId;
  state.messageScrollPinned = true;
  elements.composerError.textContent = "";

  if (isMobileLayout()) {
    navigateTo(APP_PATH, getAppChatHistoryState(nextChatId), {
      replace: !shouldPushHistory,
    });
  }

  render();

  if (focusComposerAfter) {
    focusComposer();
  }
}

function closeActiveChat({ syncHistory } = { syncHistory: false }) {
  if (!state.activeChatId) {
    return;
  }

  state.activeChatId = null;
  state.renderedChatId = null;
  state.messageScrollPinned = true;
  state.forceMessageScroll = false;
  elements.composerError.textContent = "";

  if (syncHistory || isMobileLayout()) {
    navigateTo(APP_PATH, getAppListHistoryState(), { replace: true });
  }

  render();
}

function isMobileLayout() {
  return window.innerWidth <= MOBILE_LAYOUT_BREAKPOINT_PX;
}

function shouldUseMobileChatView() {
  return isMobileLayout() && Boolean(state.activeChatId);
}

function getAuthHistoryState() {
  return { screen: "auth" };
}

function getAppListHistoryState() {
  return { screen: "app-list" };
}

function getAppChatHistoryState(chatId) {
  return {
    screen: "app-chat",
    chatId,
  };
}

function getAppHistoryState() {
  return shouldUseMobileChatView()
    ? getAppChatHistoryState(state.activeChatId)
    : getAppListHistoryState();
}

function isChatHistoryState(historyState) {
  return historyState?.screen === "app-chat" && typeof historyState.chatId === "string";
}

function getHistoryChatId(chats, historyState = window.history.state) {
  if (!isMobileLayout() || !isChatHistoryState(historyState)) {
    return null;
  }

  return chats.some((chat) => chat.id === historyState.chatId)
    ? historyState.chatId
    : null;
}

function areHistoryStatesEqual(left, right) {
  if (left === right) {
    return true;
  }

  if (!left || !right) {
    return false;
  }

  return left.screen === right.screen && left.chatId === right.chatId;
}

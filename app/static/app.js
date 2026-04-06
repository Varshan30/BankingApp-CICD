const page = document.body.dataset.page;
const accountSelector = document.getElementById("accountSelector");

const state = {
  accountId: "",
};

function formatMoney(amount, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(Number(amount || 0));
}

function toReadableType(type) {
  return type
    .toLowerCase()
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function isCreditType(type) {
  return type.includes("CREDIT") || type.includes("SALARY") || type.includes("DEPOSIT");
}

function createTransactionMarkup(transactions) {
  if (!transactions.length) {
    return '<li class="tx-item"><div class="tx-desc"><strong class="tx-title">No activity yet</strong><span class="tx-time">Activity will appear here as you use your account.</span></div></li>';
  }

  return transactions
    .map((tx) => {
      const typeLabel = toReadableType(tx.type || "transaction");
      const credit = isCreditType(tx.type || "");
      const amountSign = credit ? "+" : "-";
      const amountClass = credit ? "credit" : "debit";
      const localTime = new Date(tx.timestamp).toLocaleString("en-IN");
      const amountText = `${amountSign}${formatMoney(tx.amount)}`;

      return `
        <li class="tx-item">
          <span class="tx-tag">${tx.status || "SUCCESS"}</span>
          <div class="tx-desc">
            <strong class="tx-title">${typeLabel}</strong>
            <span class="tx-time">${localTime}</span>
          </div>
          <strong class="tx-amount ${amountClass}">${amountText}</strong>
        </li>
      `;
    })
    .join("");
}

function setFeedback(target, text, isError = false) {
  if (!target) {
    return;
  }
  target.textContent = text;
  target.style.borderColor = isError ? "#e7beb8" : "#d5e8f8";
  target.style.background = isError ? "#fff2f0" : "#f4f9fe";
  target.style.color = isError ? "#8f2c1f" : "#1e4f71";
}

function setSelectorError(message) {
  accountSelector.innerHTML = `<option value="" disabled selected>${message}</option>`;
}

async function fetchJson(url, options = {}) {
  const requestOptions = {
    cache: "no-store",
    ...options,
  };

  const response = await fetch(url, requestOptions);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

async function fetchAccountContext(accountId, limit = 8) {
  const [account, beneficiariesResponse, transactionsResponse] = await Promise.all([
    fetchJson(`/api/v1/accounts/${encodeURIComponent(accountId)}`),
    fetchJson(`/api/v1/accounts/${encodeURIComponent(accountId)}/beneficiaries`),
    fetchJson(`/api/v1/accounts/${encodeURIComponent(accountId)}/transactions?limit=${limit}`),
  ]);

  return {
    account,
    beneficiaries: beneficiariesResponse.beneficiaries || [],
    transactions: transactionsResponse.transactions || [],
  };
}

async function initAccountSelector() {
  const data = await fetchJson("/api/v1/accounts");
  const accounts = (data.accounts || []).slice(0, 5);

  if (!accounts.length) {
    setSelectorError("No active accounts");
    throw new Error("No active accounts found");
  }

  accountSelector.innerHTML = accounts
    .map((account) => `<option value="${account.accountId}">${account.accountId} - ${account.holderName}</option>`)
    .join("");

  const persisted = localStorage.getItem("novabank.activeAccount");
  const accountExists = accounts.some((account) => account.accountId === persisted);
  const selected = accountExists ? persisted : accounts[0].accountId;

  state.accountId = selected;
  accountSelector.value = selected;
  localStorage.setItem("novabank.activeAccount", selected);
}

function renderBeneficiaryOptions(selectNode, beneficiaries) {
  if (!selectNode) {
    return;
  }

  if (!beneficiaries.length) {
    selectNode.innerHTML = "<option value=''>No payees found. Add one first.</option>";
    return;
  }

  selectNode.innerHTML = beneficiaries
    .map((b) => `<option value="${b.beneficiaryId}">${b.name} (${b.bankName})</option>`)
    .join("");
}

function attachGlobalAccountListener(onAccountChange) {
  accountSelector.addEventListener("change", async () => {
    state.accountId = accountSelector.value;
    localStorage.setItem("novabank.activeAccount", state.accountId);
    if (onAccountChange) {
      await onAccountChange();
    }
  });
}

function initHomePage() {
  const balanceValue = document.getElementById("balanceValue");
  const debitValue = document.getElementById("debitValue");
  const creditValue = document.getElementById("creditValue");
  const accountIdentity = document.getElementById("accountIdentity");
  const transactionList = document.getElementById("transactionList");
  const transferForm = document.getElementById("transferForm");
  const transferResult = document.getElementById("transferResult");
  const refreshButton = document.getElementById("refreshButton");
  const budgetForm = document.getElementById("budgetForm");
  const budgetInput = document.getElementById("monthlyBudget");
  const budgetSummary = document.getElementById("budgetSummary");
  const budgetProgressBar = document.getElementById("budgetProgressBar");
  const insightsList = document.getElementById("insightsList");

  let latestOutflow = 0;
  let latestInflow = 0;

  function getBudgetKey() {
    return `novabank.budget.${state.accountId}`;
  }

  function getBudgetAmount() {
    const currentValue = budgetInput ? budgetInput.value : 20000;
    const stored = Number(localStorage.getItem(getBudgetKey()) || currentValue || 20000);
    return stored > 0 ? stored : 20000;
  }

  function updateBudgetVisuals() {
    if (!budgetInput || !budgetSummary || !budgetProgressBar) {
      return;
    }

    const budget = getBudgetAmount();
    const usagePercent = Math.min(100, Math.round((latestOutflow / budget) * 100));
    const remaining = budget - latestOutflow;

    budgetInput.value = String(Math.round(budget));
    budgetProgressBar.style.width = `${usagePercent}%`;
    budgetProgressBar.classList.toggle("warning", usagePercent >= 80 && usagePercent < 100);
    budgetProgressBar.classList.toggle("danger", usagePercent >= 100);

    if (remaining >= 0) {
      setFeedback(
        budgetSummary,
        `Spent ${formatMoney(latestOutflow)} of ${formatMoney(budget)} (${usagePercent}%). Remaining: ${formatMoney(remaining)}.`
      );
    } else {
      setFeedback(
        budgetSummary,
        `Budget exceeded by ${formatMoney(Math.abs(remaining))}. Spent ${formatMoney(latestOutflow)} against ${formatMoney(budget)}.`,
        true
      );
    }
  }

  function renderInsights(transactions) {
    if (!insightsList) {
      return;
    }

    if (!transactions.length) {
      insightsList.innerHTML = '<li class="insight-item">No activity yet. Start by doing a transfer or bill payment.</li>';
      return;
    }

    const latestTx = transactions[0];
    const netFlow = latestInflow - latestOutflow;
    const netFlowLabel = netFlow >= 0 ? `Net positive by ${formatMoney(netFlow)}` : `Net negative by ${formatMoney(Math.abs(netFlow))}`;

    const billPayments = transactions.filter((tx) => (tx.type || "").includes("BILL")).length;
    const cardOps = transactions.filter((tx) => (tx.type || "").includes("CARD")).length;

    insightsList.innerHTML = [
      `<li class="insight-item">${netFlowLabel} in recent activity.</li>`,
      `<li class="insight-item">Most recent transaction: ${toReadableType(latestTx.type || "Transaction")} on ${new Date(latestTx.timestamp).toLocaleString("en-IN")}.</li>`,
      `<li class="insight-item">Bill payments in recent set: ${billPayments}. Card operations: ${cardOps}.</li>`,
    ].join("");
  }

  async function refreshHome() {
    try {
      const context = await fetchAccountContext(state.accountId, 8);
      const outflow = context.transactions
        .filter((tx) => !isCreditType(tx.type || ""))
        .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);
      const inflow = context.transactions
        .filter((tx) => isCreditType(tx.type || ""))
        .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);

      latestOutflow = outflow;
      latestInflow = inflow;

      balanceValue.textContent = formatMoney(context.account.balance, context.account.currency);
      debitValue.textContent = formatMoney(outflow, context.account.currency);
      creditValue.textContent = formatMoney(inflow, context.account.currency);
      accountIdentity.textContent = `${context.account.holderName} | ${context.account.accountType} | ${context.account.maskedNumber}`;
      transactionList.innerHTML = createTransactionMarkup(context.transactions);
      updateBudgetVisuals();
      renderInsights(context.transactions);
    } catch (error) {
      setFeedback(transferResult, `Unable to load account data: ${String(error.message || error)}`, true);
      accountIdentity.textContent = "Unable to load account profile";
      balanceValue.textContent = "Rs --";
      debitValue.textContent = "Rs --";
      creditValue.textContent = "Rs --";
    }
  }

  if (budgetForm && budgetInput && budgetSummary) {
    budgetForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const budget = Number(budgetInput.value);
      if (budget <= 0) {
        setFeedback(budgetSummary, "Monthly budget must be greater than 0.", true);
        return;
      }
      localStorage.setItem(getBudgetKey(), String(Math.round(budget)));
      updateBudgetVisuals();
    });
  }

  transferForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      fromAccount: state.accountId,
      toAccount: document.getElementById("toAccount").value.trim(),
      amount: Number(document.getElementById("amount").value),
    };

    if (!payload.toAccount || payload.amount <= 0) {
      setFeedback(transferResult, "Enter a valid destination account and amount.", true);
      return;
    }

    if (payload.toAccount === payload.fromAccount) {
      setFeedback(transferResult, "Source and destination account cannot be the same.", true);
      return;
    }

    try {
      await fetchJson("/api/v1/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setFeedback(transferResult, `Transfer completed: ${formatMoney(payload.amount)} sent to ${payload.toAccount}.`);
      transferForm.reset();
      await refreshHome();
    } catch (error) {
      setFeedback(transferResult, `Transfer failed: ${String(error.message || error)}`, true);
    }
  });

  refreshButton.addEventListener("click", refreshHome);
  attachGlobalAccountListener(refreshHome);

  // Keep Home balances and activity current even when data changes from other pages.
  const homeAutoRefreshId = window.setInterval(refreshHome, 15000);
  window.addEventListener("focus", refreshHome);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      refreshHome();
    }
  });
  window.addEventListener("beforeunload", () => {
    window.clearInterval(homeAutoRefreshId);
  });

  refreshHome();
}

function initTransactionsPage() {
  const transactionsList = document.getElementById("transactionsPageList");
  const summaryNode = document.getElementById("transactionsSummary");
  const refreshButton = document.getElementById("transactionsRefreshButton");
  const limitInput = document.getElementById("transactionsLimit");

  async function refreshTransactions() {
    try {
      const limit = Math.max(5, Math.min(100, Number(limitInput.value || 20)));
      const context = await fetchAccountContext(state.accountId, limit);
      transactionsList.innerHTML = createTransactionMarkup(context.transactions);

      const totalDebit = context.transactions
        .filter((tx) => !isCreditType(tx.type || ""))
        .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);

      const totalCredit = context.transactions
        .filter((tx) => isCreditType(tx.type || ""))
        .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);

      summaryNode.textContent = `Showing ${context.transactions.length} transactions. Credits: ${formatMoney(totalCredit)} | Debits: ${formatMoney(totalDebit)}.`;
    } catch (error) {
      summaryNode.textContent = `Unable to load transactions: ${String(error.message || error)}`;
    }
  }

  refreshButton.addEventListener("click", refreshTransactions);
  limitInput.addEventListener("change", refreshTransactions);
  attachGlobalAccountListener(refreshTransactions);
  refreshTransactions();
}

function initBillsPage() {
  const billPaymentForm = document.getElementById("billPaymentForm");
  const beneficiaryForm = document.getElementById("beneficiaryForm");
  const billBeneficiaryId = document.getElementById("billBeneficiaryId");
  const billPaymentResult = document.getElementById("billPaymentResult");
  const beneficiaryResult = document.getElementById("beneficiaryResult");

  async function refreshBeneficiaries() {
    try {
      const context = await fetchAccountContext(state.accountId, 5);
      renderBeneficiaryOptions(billBeneficiaryId, context.beneficiaries);
    } catch (error) {
      setFeedback(billPaymentResult, `Unable to load payees: ${String(error.message || error)}`, true);
    }
  }

  billPaymentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      accountId: state.accountId,
      beneficiaryId: billBeneficiaryId.value,
      billerName: document.getElementById("billerName").value.trim(),
      amount: Number(document.getElementById("billAmount").value),
    };

    if (!payload.beneficiaryId || !payload.billerName || payload.amount <= 0) {
      setFeedback(billPaymentResult, "Please enter valid bill payment details.", true);
      return;
    }

    try {
      await fetchJson("/api/v1/bill-payments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setFeedback(billPaymentResult, `Bill paid successfully: ${formatMoney(payload.amount)} to ${payload.billerName}.`);
      billPaymentForm.reset();
      await refreshBeneficiaries();
    } catch (error) {
      setFeedback(billPaymentResult, `Bill payment failed: ${String(error.message || error)}`, true);
    }
  });

  beneficiaryForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      name: document.getElementById("beneficiaryName").value.trim(),
      accountNumber: document.getElementById("beneficiaryNumber").value.trim(),
      bankName: document.getElementById("beneficiaryBank").value.trim(),
    };

    if (!payload.name || !payload.accountNumber || !payload.bankName) {
      setFeedback(beneficiaryResult, "All payee fields are required.", true);
      return;
    }

    try {
      await fetchJson(`/api/v1/accounts/${encodeURIComponent(state.accountId)}/beneficiaries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setFeedback(beneficiaryResult, `Payee added: ${payload.name} (${payload.bankName}).`);
      beneficiaryForm.reset();
      await refreshBeneficiaries();
    } catch (error) {
      setFeedback(beneficiaryResult, `Failed to add payee: ${String(error.message || error)}`, true);
    }
  });

  attachGlobalAccountListener(refreshBeneficiaries);
  refreshBeneficiaries();
}

function initGiftCardsPage() {
  const catalogNode = document.getElementById("giftCardCatalog");
  const selector = document.getElementById("giftCardSelector");
  const amountInput = document.getElementById("giftCardAmount");
  const form = document.getElementById("giftCardForm");
  const result = document.getElementById("giftCardResult");
  let catalog = [];

  function syncAmount() {
    const selected = catalog.find((item) => item.catalogId === selector.value);
    amountInput.value = selected ? String(selected.amount) : "";
  }

  async function loadCatalog() {
    try {
      const data = await fetchJson("/api/v1/gift-cards/catalog");
      catalog = data.giftCards || [];

      selector.innerHTML = catalog
        .map((item) => `<option value="${item.catalogId}">${item.brand} - ${item.title}</option>`)
        .join("");

      catalogNode.innerHTML = catalog
        .map(
          (item) => `
            <article class="catalog-item">
              <p class="summary-label">${item.brand}</p>
              <h3>${item.title}</h3>
              <p class="summary-value small">${formatMoney(item.amount)}</p>
            </article>
          `
        )
        .join("");

      syncAmount();
    } catch (error) {
      setFeedback(result, `Unable to load gift card catalog: ${String(error.message || error)}`, true);
    }
  }

  selector.addEventListener("change", syncAmount);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      accountId: state.accountId,
      catalogId: selector.value,
      amount: Number(amountInput.value),
    };

    try {
      const response = await fetchJson("/api/v1/gift-cards/purchase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setFeedback(result, `Gift card purchased. Voucher code: ${response.voucherCode}. Amount: ${formatMoney(payload.amount)}.`);
    } catch (error) {
      setFeedback(result, `Gift card purchase failed: ${String(error.message || error)}`, true);
    }
  });

  attachGlobalAccountListener();
  loadCatalog();
}

function initCardsPage() {
  const cardsList = document.getElementById("cardsList");
  const refreshButton = document.getElementById("cardsRefreshButton");
  const addCardForm = document.getElementById("addCardForm");
  const addCardResult = document.getElementById("addCardResult");

  async function refreshCards() {
    try {
      const data = await fetchJson(`/api/v1/accounts/${encodeURIComponent(state.accountId)}/cards`);
      const cards = data.cards || [];

      if (!cards.length) {
        cardsList.innerHTML = '<p class="hint">No cards are available for this account.</p>';
        return;
      }

      cardsList.innerHTML = cards
        .map(
          (card) => `
            <article class="card-control-item">
              <h3>${card.cardType} Card •••• ${card.last4}</h3>
              <p class="hint">Network: ${card.network} | Status: ${card.status}</p>
              <p class="hint">Daily limit: ${formatMoney(card.dailyLimit)}</p>
              <div class="card-actions">
                <button class="button ghost" data-action="toggle-status" data-id="${card.cardId}" data-status="${card.status}">${card.status === "ACTIVE" ? "Block card" : "Unblock card"}</button>
                <button class="button ghost" data-action="raise-limit" data-id="${card.cardId}" data-limit="${card.dailyLimit}">Increase limit by Rs 1000</button>
              </div>
            </article>
          `
        )
        .join("");
    } catch (error) {
      cardsList.innerHTML = `<p class="hint">Unable to load cards: ${String(error.message || error)}</p>`;
    }
  }

  cardsList.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    const action = target.dataset.action;
    const cardId = target.dataset.id;
    if (!action || !cardId) {
      return;
    }

    try {
      if (action === "toggle-status") {
        const current = target.dataset.status || "ACTIVE";
        const next = current === "ACTIVE" ? "BLOCKED" : "ACTIVE";
        await fetchJson(`/api/v1/cards/${encodeURIComponent(cardId)}/status`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: next }),
        });
      }

      if (action === "raise-limit") {
        const limit = Number(target.dataset.limit || 0) + 1000;
        await fetchJson(`/api/v1/cards/${encodeURIComponent(cardId)}/limit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dailyLimit: limit }),
        });
      }

      await refreshCards();
    } catch (error) {
      cardsList.innerHTML = `<p class="hint">Card update failed: ${String(error.message || error)}</p>`;
    }
  });

  refreshButton.addEventListener("click", refreshCards);

  addCardForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      last4: document.getElementById("newCardLast4").value.trim(),
      cardType: document.getElementById("newCardType").value,
      network: document.getElementById("newCardNetwork").value,
      dailyLimit: Number(document.getElementById("newCardLimit").value),
    };

    if (!/^\d{4}$/.test(payload.last4)) {
      setFeedback(addCardResult, "Last 4 digits must be exactly 4 numbers.", true);
      return;
    }

    if (payload.dailyLimit <= 0) {
      setFeedback(addCardResult, "Daily limit must be greater than 0.", true);
      return;
    }

    try {
      await fetchJson(`/api/v1/accounts/${encodeURIComponent(state.accountId)}/cards`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      setFeedback(addCardResult, `Card ending ${payload.last4} added successfully.`);
      addCardForm.reset();
      document.getElementById("newCardLimit").value = "10000";
      await refreshCards();
    } catch (error) {
      setFeedback(addCardResult, `Could not add card: ${String(error.message || error)}`, true);
    }
  });

  attachGlobalAccountListener(refreshCards);
  refreshCards();
}

async function bootstrap() {
  try {
    await initAccountSelector();
  } catch (error) {
    setSelectorError("Unable to load accounts");
    return;
  }

  if (page === "home") {
    initHomePage();
  }
  if (page === "transactions") {
    initTransactionsPage();
  }
  if (page === "pay-bills") {
    initBillsPage();
  }
  if (page === "gift-cards") {
    initGiftCardsPage();
  }
  if (page === "cards") {
    initCardsPage();
  }
}

bootstrap();

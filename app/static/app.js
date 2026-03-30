const accountForm = document.getElementById("accountForm");
const transferForm = document.getElementById("transferForm");
const accountResult = document.getElementById("accountResult");
const transferResult = document.getElementById("transferResult");

function showResult(target, payload) {
  target.textContent = JSON.stringify(payload, null, 2);
}

accountForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const accountId = document.getElementById("accountId").value.trim();

  if (!accountId) {
    showResult(accountResult, { error: "accountId is required" });
    return;
  }

  try {
    const response = await fetch(`/api/v1/accounts/${encodeURIComponent(accountId)}`);
    const data = await response.json();
    showResult(accountResult, data);
  } catch (error) {
    showResult(accountResult, { error: "failed to fetch account", details: String(error) });
  }
});

transferForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    fromAccount: document.getElementById("fromAccount").value.trim(),
    toAccount: document.getElementById("toAccount").value.trim(),
    amount: Number(document.getElementById("amount").value),
  };

  try {
    const response = await fetch("/api/v1/transfer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    showResult(transferResult, data);
  } catch (error) {
    showResult(transferResult, { error: "failed to execute transfer", details: String(error) });
  }
});

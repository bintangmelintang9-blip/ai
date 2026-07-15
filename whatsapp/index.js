const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

async function startBot() {
    const { state, saveCreds } =
        await useMultiFileAuthState("./auth_info");

    const { version } =
        await fetchLatestBaileysVersion();

    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        browser: ["HusnanAI", "Chrome", "1.0.0"]
    });

    sock.ev.on("creds.update", saveCreds);

    if (!sock.authState.creds.registered) {
        const phoneNumber = process.env.PHONE_NUMBER;

        if (!phoneNumber) {
            console.log("❌ PHONE_NUMBER belum diisi");
            process.exit(1);
        }

        if (!sock.authState.creds.registered) {

    const phoneNumber = process.env.PHONE_NUMBER;

    if (!phoneNumber) {
        throw new Error("PHONE_NUMBER belum diisi");
    }

    setTimeout(async () => {
        try {
            const code =
                await sock.requestPairingCode(phoneNumber);

            console.log("=================================");
            console.log("PAIRING CODE:", code);
            console.log("=================================");
        } catch (err) {
            console.error("PAIRING ERROR:", err);
        }
    }, 10000);
}

    sock.ev.on("connection.update", async (update) => {

    const { connection } = update;

    console.log(update);

    if (connection === "open") {
        console.log("✅ WhatsApp Connected");
    }
});

        if (connection === "close") {
            const shouldReconnect =
                lastDisconnect?.error?.output?.statusCode !==
                DisconnectReason.loggedOut;

            console.log("🔄 Reconnecting...");

            if (shouldReconnect) {
                startBot();
            }
        }
    });

    sock.ev.on("messages.upsert", async ({ messages }) => {
        try {
            const msg = messages[0];

            if (!msg.message) return;
            if (msg.key.fromMe) return;

            const text =
                msg.message.conversation ||
                msg.message.extendedTextMessage?.text;

            if (!text) return;

            const axios = require("axios");

            const res = await axios.post(
                process.env.AI_API_URL || "http://127.0.0.1:5000/chat",
                {
                    user_id: msg.key.remoteJid,
                    message: text
                }
            );

            await sock.sendMessage(
                msg.key.remoteJid,
                {
                    text: res.data.reply
                }
            );

        } catch (err) {
            console.error(err);
        }
    });
}

startBot();

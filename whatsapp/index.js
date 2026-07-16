const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

const P = require("pino");
const axios = require("axios");

console.log("=== WHATSAPP BOT STARTING ===");

async function startBot() {

    try {

        console.log("=== START BOT CALLED ===");

        const { state, saveCreds } =
            await useMultiFileAuthState("./auth_info");

        console.log("=== AUTH LOADED ===");

        const { version } =
            await fetchLatestBaileysVersion();

        console.log("WA VERSION:", version);

        const sock = makeWASocket({
            version,
            auth: state,
            printQRInTerminal: false,
            logger: P({ level: "silent" }),
            browser: ["Ubuntu", "Chrome", "22.04"]
        });

        sock.ev.on("creds.update", saveCreds);

        let pairingRequested = false;

        sock.ev.on(
            "connection.update",
            async (update) => {

                const {
                    connection,
                    lastDisconnect
                } = update;

                console.log(
                    "Connection:",
                    connection
                );

                console.log(
                    "Registered:",
                    sock.authState.creds.registered
                );

                if (
                    !sock.authState.creds.registered &&
                    !pairingRequested
                ) {

                    pairingRequested = true;

                    try {

                        const phoneNumber =
                            process.env.PHONE_NUMBER
                                .replace(/\D/g, "");

                        console.log(
                            "📱 Using number:",
                            phoneNumber
                        );

                        if (!phoneNumber) {

                            console.log(
                                "❌ PHONE_NUMBER belum diisi"
                            );

                            return;
                        }

                        console.log(
                            "⏳ Menunggu pairing..."
                        );

                        await new Promise(
                            resolve =>
                                setTimeout(
                                    resolve,
                                    15000
                                )
                        );

                        const code =
                            await sock.requestPairingCode(
                                phoneNumber
                            );

                        console.log("");
                        console.log(
                            "===================="
                        );
                        console.log(
                            "PAIRING CODE:"
                        );
                        console.log(code);
                        console.log(
                            "===================="
                        );
                        console.log("");

                    } catch (err) {

                        pairingRequested = false;

                        console.error(
                            "PAIRING ERROR:"
                        );

                        console.error(err);
                    }
                }

                if (
                    connection === "open"
                ) {

                    console.log(
                        "✅ WhatsApp Connected"
                    );

                    console.log(
                        "Registered:",
                        sock.authState.creds.registered
                    );
                }

                if (
                    connection === "close"
                ) {

                    const statusCode =
                        lastDisconnect?.error
                            ?.output
                            ?.statusCode;

                    console.log(
                        "🔄 Connection Closed:",
                        statusCode
                    );

                    const shouldReconnect =
                        statusCode !==
                        DisconnectReason.loggedOut;

                    if (
                        shouldReconnect
                    ) {

                        console.log(
                            "♻️ Reconnecting..."
                        );

                        setTimeout(
                            () => {
                                startBot();
                            },
                            5000
                        );
                    }
                }
            }
        );

        sock.ev.on(
            "messages.upsert",
            async ({ messages }) => {

                try {

                    const msg =
                        messages?.[0];

                    if (!msg) return;
                    if (!msg.message) return;
                    if (msg.key.fromMe)
                        return;

                    const text =
                        msg.message
                            .conversation ||
                        msg.message
                            .extendedTextMessage
                            ?.text;

                    if (!text) return;

                    console.log(
                        "📩 Message:",
                        text
                    );

                    const aiUrl =
                        process.env.AI_API_URL ||
                        "http://127.0.0.1:5000/chat";

                    const response =
                        await axios.post(
                            aiUrl,
                            {
                                user_id:
                                    msg.key.remoteJid,
                                message:
                                    text
                            },
                            {
                                timeout: 60000
                            }
                        );

                    const reply =
                        response?.data
                            ?.reply ||
                        "Maaf, AI tidak memberikan jawaban.";

                    await sock.sendMessage(
                        msg.key.remoteJid,
                        {
                            text: reply
                        }
                    );

                } catch (err) {

                    console.error(
                        "MESSAGE ERROR:"
                    );

                    console.error(err);

                    try {

                        await sock.sendMessage(
                            msg.key.remoteJid,
                            {
                                text:
                                    "Terjadi kesalahan saat memproses pesan."
                            }
                        );

                    } catch {}
                }
            }
        );

    } catch (err) {

        console.error(
            "START BOT ERROR:"
        );

        console.error(err);

        setTimeout(
            () => {
                startBot();
            },
            10000
        );
    }
}

process.on(
    "uncaughtException",
    console.error
);

process.on(
    "unhandledRejection",
    console.error
);

startBot();

const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

const axios = require("axios");

console.log("=== WHATSAPP BOT STARTING ===");

async function startBot() {

    console.log("=== START BOT CALLED ===");

    const { state, saveCreds } =
        await useMultiFileAuthState("./auth_info");

    console.log("=== AUTH LOADED ===");

    const { version } =
        await fetchLatestBaileysVersion();

    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        browser: ["HusnanAI", "Chrome", "1.0.0"]
    });

    sock.ev.on("creds.update", saveCreds);

    let pairingRequested = false;

    sock.ev.on("connection.update", async (update) => {

        const { connection, lastDisconnect } = update;

        console.log("Connection:", connection);

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

                await new Promise(resolve =>
                    setTimeout(resolve, 15000)
                );

                const code =
                    await sock.requestPairingCode(
                        phoneNumber
                    );

                console.log("");
                console.log("====================");
                console.log("PAIRING CODE:");
                console.log(code);
                console.log("====================");
                console.log("");

            } catch (err) {

                pairingRequested = false;

                console.error(
                    "PAIRING ERROR FULL:"
                );

                console.error(err);
                console.error(err?.message);
                console.error(err?.stack);

                try {
                    console.error(
                        JSON.stringify(
                            err,
                            null,
                            2
                        )
                    );
                } catch {}
            }
        }

        if (connection === "open") {

            console.log(
                "✅ WhatsApp Connected"
            );

            console.log(
                "Registered:",
                sock.authState.creds.registered
            );
        }

        if (connection === "close") {

            const shouldReconnect =
                lastDisconnect?.error?.output?.statusCode !==
                DisconnectReason.loggedOut;

            console.log(
                "🔄 Connection Closed"
            );

            if (shouldReconnect) {

                setTimeout(() => {
                    startBot();
                }, 5000);
            }
        }
    });

    sock.ev.on(
        "messages.upsert",
        async ({ messages }) => {

            try {

                const msg = messages[0];

                if (!msg.message) return;
                if (msg.key.fromMe) return;

                const text =
                    msg.message.conversation ||
                    msg.message.extendedTextMessage?.text;

                if (!text) return;

                console.log(
                    "📩 Message:",
                    text
                );

                const res = await axios.post(
                    process.env.AI_API_URL ||
                    "http://127.0.0.1:5000/chat",
                    {
                        user_id:
                            msg.key.remoteJid,
                        message: text
                    }
                );

                await sock.sendMessage(
                    msg.key.remoteJid,
                    {
                        text:
                            res.data.reply ||
                            "Maaf terjadi kesalahan."
                    }
                );

            } catch (err) {

                console.error(
                    "MESSAGE ERROR:"
                );

                console.error(err);
            }
        }
    );
}

process.on(
    "uncaughtException",
    console.error
);

process.on(
    "unhandledRejection",
    console.error
);

startBot().catch(console.error);

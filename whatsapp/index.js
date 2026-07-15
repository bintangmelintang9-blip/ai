const {
default: makeWASocket,
useMultiFileAuthState,
DisconnectReason,
fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

const axios = require("axios");

async function startBot() {


const { state, saveCreds } =
    await useMultiFileAuthState("./auth_info");

const { version } =
    await fetchLatestBaileysVersion();
async function startBot() {

    console.log("=== START BOT CALLED ===");

    const { state, saveCreds } =
        await useMultiFileAuthState("./auth_info");

    console.log("=== AUTH LOADED ===");

    const { version } =
        await fetchLatestBaileysVersion();

    console.log("=== LOADING BAILEYS ===");

    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        browser: ["HusnanAI", "Chrome", "1.0.0"]
    });
const sock = makeWASocket({
    version,
    auth: state,
    printQRInTerminal: false,
    browser: ["HusnanAI", "Chrome", "1.0.0"]
});

sock.ev.on("creds.update", saveCreds);

let pairingRequested = false;

sock.ev.on("connection.update", async (update) => {

    const {
        connection,
        lastDisconnect
    } = update;

    console.log("Connection:", connection);

    if (
        !sock.authState.creds.registered &&
        !pairingRequested
    ) {

        pairingRequested = true;

        try {

            const phoneNumber =
                process.env.PHONE_NUMBER;

            if (!phoneNumber) {
                console.log(
                    "❌ PHONE_NUMBER belum diisi"
                );
                return;
            }

            await new Promise(resolve =>
                setTimeout(resolve, 15000)
            );

            const code =
                await sock.requestPairingCode(
                    phoneNumber
                );

            console.log("");
            console.log(
                "========================="
            );
            console.log(
                "PAIRING CODE:"
            );
            console.log(code);
            console.log(
                "========================="
            );
            console.log("");

        } catch (err) {

            pairingRequested = false;

            console.error(
                "PAIRING ERROR:",
                err
            );
        }
    }

    if (connection === "open") {

        console.log(
            "✅ WhatsApp Connected"
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
                        res.data.reply
                }
            );

        } catch (err) {

            console.error(
                "MESSAGE ERROR:",
                err
            );
        }
    }
);


}

startBot().catch(console.error);

}

startBot();

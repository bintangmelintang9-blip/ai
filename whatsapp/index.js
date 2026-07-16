const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

const axios = require("axios");

console.log("=== HUSNAN AI STARTING ===");

async function startBot() {
    try {
        const { state, saveCreds } =
            await useMultiFileAuthState("./auth_info");

        const { version } =
            await fetchLatestBaileysVersion();

        console.log(
            "Using Baileys Version:",
            version
        );

        const sock = makeWASocket({
            version,
            auth: state,
            printQRInTerminal: false,
            browser: [
                "HusnanAI",
                "Chrome",
                "1.0.0"
            ]
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
                    "Connection Status:",
                    connection
                );

                if (
                    !sock.authState.creds.registered &&
                    !pairingRequested
                ) {

                    pairingRequested = true;

                    try {

                        let phoneNumber =
                            process.env.PHONE_NUMBER || "";

                        phoneNumber =
                            phoneNumber
                                .replace(/\D/g, "")
                                .replace(/^0/, "62");

                        if (!phoneNumber) {

                            console.log(
                                "❌ PHONE_NUMBER belum diisi"
                            );

                            return;
                        }

                        console.log(
                            "📱 Nomor:",
                            phoneNumber
                        );

                        console.log(
                            "⏳ Meminta pairing code..."
                        );

                        await new Promise(
                            resolve =>
                                setTimeout(
                                    resolve,
                                    5000
                                )
                        );

                       

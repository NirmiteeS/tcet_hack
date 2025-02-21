import dotenv from "dotenv"
dotenv.config()

import connectDB from "./db/db.js"
import { app } from "./app.js"
import { Server } from "socket.io"
import socketUtility from "./sockets.js"

const PORT = process.env.PORT || 3000

connectDB()
.then(() => {
    app.listen(PORT, () => {
        console.log(`Server listening on PORT ${PORT}`)
    })

    // const io = new Server(server, {
    //     pingTimeout: 60000,
    //     cors: {
    //         origin: true,
    //         credentials: true
    //     }
    // })

    // io.on("connection", (socket) => {
    //     socketUtility(socket)
    // })
})
.catch((err) => {
    console.log("Error in connecting MongoDB ", err)
})
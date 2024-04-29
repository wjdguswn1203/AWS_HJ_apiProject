const express = require('express')
const bodyParser = require('body-parser')
const pool = require("../pool");

const app = express()

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: false }))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

app.get('/Hello', (req, res) => {
    res.send("Hello World")
})

app.get('/selectPyeup', async (req, res) => {
    const [data, fileds] = await pool.query("select * from pyeup")
    console.log(data);
    res.send(data);
})

module.exports = app;

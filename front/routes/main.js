const express = require('express')
const bodyParser = require('body-parser')
const pool = require("../pool");

const app = express()

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: false }))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

app.get('/', (req, res) => {
    res.redirect('index.html');
})

app.get('/selectPyeup', async (req, res) => {
    const [data, fileds] = await pool.query("select * from pyeup");
    // console.log(data);

    res.redirect('selectPyeup.html');
})

module.exports = app;

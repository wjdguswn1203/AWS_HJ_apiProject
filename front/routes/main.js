const express = require("express");
const bodyParser = require('body-parser');
const pool = require("../pool.js");
const axios = require("axios");
const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));


app.get('/', (req, res) => {
    res.redirect('index.html');
})

app.get("/selectPyeup", async (req, res) => {
    const year = req.query.year;
    try {
        let tmp = await pool.query("select * from pyeup where year=?", [year]);
        console.log(tmp[0].length)
        if (tmp[0].length == 0) {
            const response = await axios.get("http://0.0.0.0:3500/insertSQL?year=" + String(year));
            tmp = response.data;
        }
        tmp = await pool.query("select * from pyeup where year=? order by count desc",[year]);
        var result = {
            "result code": res.statusCode,
            result: tmp[0],
        };
        res.send(result);
    } catch (error) {
        console.error(error);
        res.status(500).send("Internal Server Error");
    }
});


app.get("/selectPyeupApi", async (req, res) => {
    try {
        let tmp = await pool.query("select * from pyeupapi;");
        if (tmp[0].length == 0) {
            const response = await axios.get("http://0.0.0.0:3500/getPyeupApiSql");
            tmp = response.data;
        }
        tmp = await pool.query("SELECT * FROM pyeupapi WHERE count > 0 ORDER BY count DESC;");
        var result = {
            "result code": res.statusCode,
            result: tmp[0],
        };
        res.send(result);
    } catch (error) {
        console.error(error);
        res.status(500).send("Internal Server Error");
    }
});
module.exports = app;

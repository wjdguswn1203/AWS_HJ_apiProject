const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('sync-mysql');
const env = require('dotenv').config({ path: "../../.env" });

var connection = new mysql({
    host: process.env.host,
    user: process.env.user,
    password: process.env.password,
    database: process.env.database
});

const app = express()

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// function template_nodata(res) {
//     res.writeHead(200);
//     var template = `
//     <!doctype html>
//     <html>
//     <head>
//         <title>Result</title>
//         <meta charset="utf-8">
//         <link type="text/css" rel="stylesheet" href="mainstyle.css" />
//     </head>
//     <body>
//         <h3>데이터가 존재하지 않습니다.</h3>
//     </body>
//     </html>
//     `;
//     res.end(template);
// }

app.get('/hello', (req, res) => {
    res.send('Hello World~!!');
})

// login
// app.post('/login', (req, res) => {
//     const { id, pw } = req.body;
//     const result = connection.query("select * from user where userid=? and passwd=?", [id, pw]);
//     // console.log(result);
//     if (result.length == 0) {
//         res.redirect('error.html')
//     }
//     if (id == 'admin' || id == 'root') {
//         console.log(id + " => Administrator Logined")
//         res.redirect('member.html?id=' + id);
//     } else {
//         console.log(id + " => User Logined")
//         res.redirect('user.html?id=' + id)
//     }
// })

module.exports = app;

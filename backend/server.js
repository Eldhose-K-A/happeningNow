var express = require('express');
var request = require('request');

var app = express();

app.set('view engine', 'ejs');
app.use(express.static('public'));
//--------------------------------------------------------------------------------------------------
app.get('/', function (req, res) {
    console.log("Connected to :-> /");
    res.redirect('/index.html');
});
//--------------------------------------------------------------------------------------------------
app.get('/get_coin', function (req, res) {
    console.log("Connected to :-> /get_coin");
    request('http://10.90.90.79:5000/get_chain',function(err1,res1,body1){
		if(!err1){
			console.log("HTTP Request to 'http://10.90.90.79:5000/get_chain' -> Okay");
			res.end(body1);
		}
		else{
			console.log("HTTP Request to 'http://10.90.90.79:5000/get_chain' -> Not Okay");
			res.end("ERROR");
		}
	});
});
//--------------------------------------------------------------------------------------------------
var server = app.listen(3000, function () {
    console.log("Server Started at port 3000 !.......");
});
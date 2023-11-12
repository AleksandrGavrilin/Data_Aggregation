![](img_for_readme/img.jpg)
_____
Project for aggregation of statistical data on salaries of company employees by time periods using a MongoDB.
_____
### <span style='color:rgb(165, 42, 42)'> Main functionality of the program. </span>
The user sends a request to the telegram bot in accordance with the specified form.
Which contains fields such as:
- date from ("dt_form");
- date to ("dt_upto");
- grouping by: hour; day or month ("group_type").

At the output, the algorithm generates a response containing:<br/>
An array of aggregated data (in the form of a data set and in the form of labels).

### <span style='color:rgb(165, 42, 42)'> Below is an example of a request and response: </span>

**Request:**<br/>
{<br/>
   "dt_from": "2022-02-01T00:00:00",<br/>
   "dt_upto": "2022-02-02T00:00:00",<br/>
   "group_type": "hour"<br/>
}<br/>

**Response:**<br/>
{"dataset":<br/>
[8177, 8407, 4868, 7706, 8353,<br/>
7143, 6062, 11800, 4077, 8820, 4788,<br/>
11045, 13048, 2729, 4038, 9888, 7490,<br/>
11644, 11232, 12177, 2741, 5341, 8730, 4718],<br/>
"labels":<br/>
["2022-02-01T00:00:00", "2022-02-01T01:00:00", "2022-02-01T02:00:00",<br/> 
"2022-02-01T03:00:00", "2022-02-01T04:00:00", "2022-02-01T05:00:00",<br/>
"2022-02-01T06:00:00", "2022-02-01T07:00:00", "2022-02-01T08:00:00",<br/> 
"2022-02-01T09:00:00", "2022-02-01T10:00:00", "2022-02-01T11:00:00",<br/>
"2022-02-01T12:00:00", "2022-02-01T13:00:00", "2022-02-01T14:00:00",<br/>
"2022-02-01T15:00:00", "2022-02-01T16:00:00", "2022-02-01T17:00:00",<br/>
"2022-02-01T18:00:00", "2022-02-01T19:00:00", "2022-02-01T20:00:00",<br/>
"2022-02-01T21:00:00", "2022-02-01T22:00:00", "2022-02-01T23:00:00"]}

### <span style='color:rgb(165, 42, 42)'> Usage. </span>
1. download project;
2. start the Mongo database;
3. create telegram bot with BotFather, and copy token;
4. replace the token and the path to the database in the main.py file;
5. run program on computer or server.
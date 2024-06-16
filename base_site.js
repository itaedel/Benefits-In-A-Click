const express = require('express');
const bodyParser = require('body-parser');
const {Pool} = require('pg');

const app = express();
const cors = require('cors');
app.use(cors());
app.use(bodyParser.json());


const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'postgres',
    password: '1234',
    port: 5432,

});

const max_query = 'SELECT *, \'max_company\' as company FROM benefits_max WHERE (benefit_name LIKE $1 or benefit_details LIKE $1)';
const isracard_query = 'SELECT *, \'isracard\' AS company FROM benefits_isracard WHERE (benefit_name LIKE $1 or benefit_details LIKE $1)';
const amex_query = 'SELECT *, \'amex\' AS company FROM benefits_amex WHERE (benefit_name LIKE $1 or benefit_details LIKE $1)';

app.post('/search', async (req, res) => {
    try {
        console.log('Awaiting client connection...');
        const client = await pool.connect();
        console.log('Client connected')
        console.log('search_title is: ', req.body.search_title);
        let query_params = []
        const search_title = req.body.search_title;
        const req_category = req.body.category;
        let benefit_queries = [];
        if (req.body.filter_max) {
            benefit_queries.push(max_query);
        }
        if (req.body.filter_isracard) {
            benefit_queries.push(isracard_query);
        }
        if (req.body.filter_amex) {
            benefit_queries.push(amex_query);
        }
        if (search_title !== "") {
            query_params.push(`%${search_title}%`)
        }
        if (req.body.category !== "") {
            benefit_queries = benefit_queries.map(query => query.replace('WHERE', `WHERE category = $${query_params.length + 1} AND`));
            query_params.push(req_category);
        }
        if (search_title === "") {
            benefit_queries = benefit_queries.map(query =>
                query.replace('(benefit_name LIKE $1 or benefit_details LIKE $1)', 'TRUE'));
        }
        const benefit_query = benefit_queries.join('\nUNION\n');
        const result = await client.query(benefit_query, query_params);
        console.log("Found " + result.rows.length + " results")
        res.json(result.rows);
        client.release();
    } catch (err) {
        console.error('Error executing query', err);
        res.status(500).send('Internal Server Error');
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

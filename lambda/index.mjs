// import file system library
import * as fs from 'node:fs';
// use file system library to include the html from index.html
const html = fs.readFileSync('index.html', { encoding: 'utf8' });

// import library for access to the DynamoDB system
import { DynamoDB } from "@aws-sdk/client-dynamodb";
// create a DynamoDB client, which is how the service is accessed
const client = new DynamoDB({});
// import library for more intuitive commands for DynamoDB
import { DynamoDBDocument } from "@aws-sdk/lib-dynamodb";
const ddbDocClient = DynamoDBDocument.from(client);

export const handler = async (event) => {
    console.log(event);
    const tableName = process.env.TABLE_NAME;
    
    // if the user submitted something (which goes in the queryStringParameters), put it in the table
    if (event.queryStringParameters) {
        // asynchronously put the given information in the table using DynamoDBDocument's more intuitive syntax
        if (event.queryStringParameters === "vote
        await ddbDocClient.put({
            TableName: tableName,
            Item: {
                ImageHash: "Test Hash 2",
                Category1: "Test value 1",
                Category2: "Test value 2",
                Category1Votes: 7,
                Category2Votes: 3
            }
        })
    }
    // create a new html data type with the information from dynamicForm
    let modifiedHtml = dynamicForm(html, event.queryStringParameters)

    // ask DynamoDB for all the items in the table and place them in tableQuery
    const tableQuery = await ddbDocClient.query({
        TableName: tableName,
        KeyConditionExpression: "ImageHash = :ImageHash",
        ExpressionAttributeValues: {
            ":ImageHash": "Test Hash 2"
        }
    });
    // change modifiedHtml to include the information from dynamicTable
    modifiedHtml = dynamicTable(modifiedHtml, tableQuery);

    const response = {
        statusCode: 200,
        headers: {
            'Content-Type': 'text/html',
        },
        body: modifiedHtml,
    };
    return response;
};

// replace {formResults} in the original index.html file with the queryStringParameters from the user's submission,
// effectively showing the user their submission
function dynamicForm(html, queryStringParameters) {
    let formres = '';
    if (queryStringParameters) {
        Object.values(queryStringParameters).forEach(val => {
            formres = formres + val + ' ';
        });
    }
    return html.replace('{formResults}', '<h4>Form Submission: ' + formres + '</h4>');
}

// replace {table} with all of the items in the DynamoDB table, showing the user the contents of the table
function dynamicTable(html, tableQuery) {
    let table = "";
    if (tableQuery.Items.length > 0) {
        for (let i = 0; i < tableQuery.Items.length; i++) {
            table = table + "<li>" + JSON.stringify(tableQuery.Items[i]) + "</li>";
        }
        table = "<pre>" + table + "</pre>";
    }
    return html.replace("{table}", "<h4>DynamoDB:</h4>" + table);
}
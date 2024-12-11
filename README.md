
# Pointless Analogies

This is an AWS CDK app written in Python that provides a website to make utterly pointless, but sometimes fun comparisons between objects. When you go to the website you're given a choice to upload an image - any image you want - which will then be stored in a database along with two randomly selected nouns. Afterwards you're shown the images that other people have uploaded along with the nouns associated with their images. It is then your task to vote on which noun you think is closest to the image.

Suppose someone uploads an image of their backpack and the nouns assigned to it are "shoe" and "car". When you see this image you would then vote on whether the backpack shown is more like a shoe or a car. Obviously the real answer is that it's neither, but you might find that you can make an argument either way. You could say it's like a shoe because it's something you wear, but you could also say it's like a car because you can use it to transport items. These are pointless analogies, but you could have some fun with it if you got into it.

## App Architecture

This app uses a serverless architecture for minimal cost and easy scalability, defined in `pointless_analogies/pointless_analogies_stack.py`. The user connects to an HTTP API from AWS API Gateway which runs a lambda function depending on the route and payload. This lambda function does any necessary backend processing and then returns the correct HTML to the user. This HTML is stored as templates in an S3 bucket with placeholder values for the API endpoint, image hash, and other runtime values. When a lambda function returns HTML to the user, it gets the template from the bucket, replaces placeholder values with the correct runtime values, and then sends it to the user.

There are several parts of this architecture:

- **S3 Buckets:** There are two S3 buckets in this architecture. One holds HTML template files, which have placeholder values for things like the API endpoint or the image hash which must be known at runtime. Every file stored in `html_templates` is automatically uploaded to this bucket upon deployment. The other bucket stores images, and each time an image is uploaded to this bucket, `generate_image_hash_function` is called.
- **HTTP API Gateway:** This is the service that allows users to connect to the app in the first place. The default endpoint calls the main page lambda function to return the correct HTML to the user for the main page. The `/vote` path calls the vote page lambda function with the image hash given in the query string parameters, returning the initial voting page for the `GET` method and submitting the payload of a vote for the `POST` method.
- **Lambda Functions:** Each call to the HTTP API calls a specific lambda function.
  - `main_page_function` gets the HTML template `image_snippet.html` and, for each entry in the DynamoDB table, fills out the file with the correct image hash and API endpoint for that image. It then replaces the placeholder value `{imagesBegin}` in `main_page.html` with the HTML snippet and repeats. After updating all the placeholder values in the main page, the updated HTML is sent to the user.
  - `vote_page_handler_function` processes which request is being sent to the `/vote` path of the endpoint. If the method is `GET` then the placeholders in `vote_page.html` are updated and the HTML is sent to the user. If the method is `POST` then the payload containing the vote choice is parsed, the DynamoDB table is updated with the user's vote, and the new vote count is returned to the user for the inline JavaScript function in the HTML to display.
  - `get_categories_function` returns two random category selections to the caller.
  - `generate_image_hash_function` is run automatically every time something is uploaded to the image bucket. It generates a unique hash for the image, places an entry with the hash in the DynamoDB table along with two random categories from `get_categories_function` and an initial vote count of 0 for both of them, and renames the image in the bucket with the unique hash.
- **DynamoDB Table:** The table holds a string as its key value which is the image hash and gets updated as described in `generate_image_hash_function` and `vote_page_handler_function`.

## Automated Deployment

This app uses CDK for automated deployment. The CDK code generates a cloudformation template, which is used to deploy the Pointless Analogies Stack. Image uploading for the purposes of testing was also automated with the `upload_S3_test_images.sh` script.

GitHub Actions was used to further simplify automated deployment. The "AWS Manual CDK Deploy" action can be run from the Actions page on the GitHub repo. This action automatically runs `cdk deploy` on a linux machine using the main branch, which deploys the current production code. Similarly, the "Manual Stack Destroy" Action can be run from GitHub to easily destroy the stack.

Continuous deployment has been implemented using GitHub Actions. When the main branch of the GitHub repository is pushed to, the "AWS Continuous Deployment" Action is automatically run. This action automatically runs `cdk deploy` on the updated code. If the stack is not currently active, however, this action will not deploy. In other words, the only action that will activate the stack if it is not yet active is "AWS Manual CDK Deploy".

## Security

Security is managed by the various grant access functions provided by CDK constructs such as `html_bucket.grant_read()` or `table.grant_read_data()`. All constructs are managed with the minimum access necessary except for the image bucket, which is publicly readable and writable because of technical difficulties implementing a pre-signed URL.

## Source Control

There is a central repository on GitHub which was used for source control. There is extensive documentation of the source control workflow in `Git-Workflow.md`.

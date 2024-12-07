
# Pointless Analogies

This is an AWS CDK app written in Python that provides a website to make utterly pointless, but sometimes fun comparisons between objects. When you go to the website you're given a choice to upload an image - any image you want - which will then be stored in a database along with two randomly selected nouns. Afterwards you're shown the images that other people have uploaded along with the nouns associated with their images. It is then your task to vote on which noun you think is closest to the image.

Suppose someone uploads an image of their backpack and the nouns assigned to it are "shoe" and "car". When you see this image you would then vote on whether the backpack shown is more like a shoe or a car. Obviously the real answer is that it's neither, but you might find that you can make an argument either way. You could say it's like a shoe because it's something you wear, but you could also say it's like a car because you can use it to transport items. These are pointless analogies, but you could have some fun with it if you got into it.

## App Architecture

This app uses a serverless architecture for minimal cost and easy scalability.

## Automated Deployment

This app uses CDK for automated deployment. The CDK code generates a cloudformation template, which is used to deploy the Pointless Analogies Stack. Image uploading for the purposes of testing was also automated with the `upload_S3_test_images.sh` script. 

GitHub Actions was used to further simplify automated deployment. The "AWS Manual CDK Deploy" action can be run from the Actions page on the GitHub repo. This action automatically runs `cdk deploy` on a linux machine using the main branch, which deploys the current production code.

Continuous deployment has been implemented using GitHub Actions. When the main branch of the GitHub repository is pushed to, the "AWS Continuous Deployment" Action is automatically run. This action automatically runs `cdk deploy` on the updated code. If the stack is not currently active, however, this action will not deploy. In other words, the only action that will activate the stack if it is not yet active is "AWS Manual CDK Deploy". 

## Security

## Source Control

# Original README for Temporary Reference

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

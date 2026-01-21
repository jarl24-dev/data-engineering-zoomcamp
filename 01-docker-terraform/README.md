## Question 1. Understanding Docker images

Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.

What's the version of `pip` in the image?

`Step 1:` Execute `docker run -it --rm --entrypoint=bash python:3.13` 
`Step 2:` Inside the container, execute `pip --version`
`Answer:` 25.3

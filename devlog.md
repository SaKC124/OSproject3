# Project 3 Devlog

## Log 1: Dec 10: 3:26pm
### Had a very late start to the project but I am going to zone in for at least 2 hours so hopefully I can make a good chunk of progress. I created the repo and python file, and moved the test.idx file to my project file to make it easier for testing. I plan to do the project in python, and I going to plan out how to approach it because I'm assuming the code will be a bit lengthy based on what we are doing.

## Log 2: Dec 10, 3:51pm
### To make it easier for me to understand my code logically and how it will be executed, I am going to have many methods implemented and helper functions that perform actions needed based on the commands I put. The main method will only take input from the user and identify the command given so that it calls the necessary functions to perform it. I'm going to create the outline of the main method first that will compose of if methods and include error handling with try if something wrong happens during execution. It will also help when I need to debug in the command line. So far the methods I know I need to implement is for insertion, search, reading/writing node, and printing. This is all I can think of for the methods for now.

## Log 3: Dec 10, 4:30pm
### I finished the outline for main and going to start with doing the insertion functionality. I think this might be long because with the insertions we will have to do splitting and other things to handle the B+ tree structure. But I fill figure it out as I work on it

## Log 4: Dec 10, 5:42pm
### I'm probably like almost 70% done with the insertion part, but I have made some changes with it mid-way through coding so that I can structure the functionality better. The action of inserting is going to be one method, and then you have a split method called when necessary that will split the node when necessary. This is to make the program run efficiently because we wouldn't need to split all the time, and it makes the insert method neat and simple. To supplement and help with that, I will add a separate functionality to shift keys and assign them to nodes that are not full, or else they would split. As I'm doing the insertionimplementation for the B+ tree, I'm also doing the B tree node structure by creating a node class.

##

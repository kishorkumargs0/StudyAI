LECTURES = [
    {
        "id": 1,
        "title": "Neural Networks: Forward and Backpropagation",
        "course": "CS 439",
        "source": "sample notes",
        "kind": "TEXT",
        "words": 198,
        "summary": (
            "A neural network is built from layers of neurons connected by weights. During a forward pass, inputs "
            "are multiplied by weights, a bias is added, and an activation function is applied. Training lowers a "
            "loss function by using backpropagation to find each weight's share of the error, then gradient descent "
            "to adjust the weights. The learning rate controls how big each update is."
        ),
        "concepts": [
            {"term": "Learning Rate", "detail": "The learning rate controls the size of each update."},
            {
                "term": "Activation Functions",
                "detail": "Functions like ReLU let the network model nonlinear relationships.",
            },
            {
                "term": "Backpropagation",
                "detail": "Uses the chain rule to find how much each weight contributed to the loss.",
            },
            {"term": "Overfitting", "detail": "When a model memorizes its training data and does poorly on new data."},
        ],
        "flashcards": [
            {"front": "The _____ controls the size of each update.", "back": "Learning Rate"},
            {
                "front": "_____ such as ReLU let the network model nonlinear relationships.",
                "back": "Activation Functions",
            },
            {
                "front": "_____ applies the chain rule to find each weight's share of the loss.",
                "back": "Backpropagation",
            },
            {"front": "_____ happens when a model memorizes its training examples.", "back": "Overfitting"},
        ],
        "quiz": [
            {
                "question": "What happens if the learning rate is too large?",
                "options": [
                    "Training gets slower",
                    "It can skip over a good solution",
                    "The loss can't be measured",
                    "Layers are removed",
                ],
                "answer": 1,
            },
            {
                "question": "Why are nonlinear activations needed?",
                "options": [
                    "They make training faster",
                    "They remove the bias",
                    "Without them, stacked layers act like one linear model",
                    "They prevent overfitting",
                ],
                "answer": 2,
            },
            {
                "question": "Which of these helps reduce overfitting?",
                "options": [
                    "Early stopping",
                    "A larger learning rate",
                    "Removing validation data",
                    "More hidden layers",
                ],
                "answer": 0,
            },
        ],
    },
    {
        "id": 2,
        "title": "Hash Tables",
        "course": "CS 112",
        "source": "sample notes",
        "kind": "TEXT",
        "words": 176,
        "summary": (
            "A hash table stores key-value pairs and supports lookup, insertion, and deletion in average constant "
            "time. A hash function maps each key to a bucket. Collisions are handled with separate chaining or open "
            "addressing. When the load factor gets too high, the table is resized and every entry is rehashed."
        ),
        "concepts": [
            {"term": "Hash Function", "detail": "Maps each key to an index in the array of buckets."},
            {"term": "Collision", "detail": "Two different keys land in the same bucket."},
            {"term": "Load Factor", "detail": "Number of stored entries divided by the number of buckets."},
            {"term": "Rehashing", "detail": "Resizing the table and moving every entry when it gets too full."},
        ],
        "flashcards": [
            {"front": "A _____ maps each key to an index in the bucket array.", "back": "Hash Function"},
            {"front": "A _____ happens when two keys map to the same index.", "back": "Collision"},
            {"front": "The _____ is entries divided by buckets.", "back": "Load Factor"},
            {
                "front": "When the table gets too full it is resized and every entry goes through _____.",
                "back": "Rehashing",
            },
        ],
        "quiz": [
            {
                "question": "What is the average time for a hash table lookup?",
                "options": ["Constant", "Logarithmic", "Linear", "Quadratic"],
                "answer": 0,
            },
            {
                "question": "Which strategy keeps a linked list in each bucket?",
                "options": ["Linear probing", "Separate chaining", "Rehashing", "Binary search"],
                "answer": 1,
            },
            {
                "question": "What is the worst case for a lookup when every key collides?",
                "options": ["Constant", "Logarithmic", "Linear", "It can't happen"],
                "answer": 2,
            },
        ],
    },
]


def find(lecture_id):
    for lecture in LECTURES:
        if lecture["id"] == lecture_id:
            return lecture
    return None

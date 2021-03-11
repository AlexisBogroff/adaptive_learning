#First import everything

import pandas as pd
import numpy as np

#Then, I will just create few functions that will be useful later to test our code

def generate_user_item_matrix(nb_quest, nb_users):

  #It takes 2 arguments : number of users and number of questions
  #This function will return a student/question matrix

    matrix_user_quest=[]

    for k in range(nb_users):
        user_score=[]
        for j in range(nb_quest):

            elements = [0,1,2,3,4]
            weights = [0.5, 0.1, 0.15, 0.15,0.1]

            score_question=np.random.choice(elements, p=weights)
            user_score.append(score_question)

        matrix_user_quest.append(user_score)

    return (matrix_user_quest)


def generate_columns_name(nb_quest):

    #This function will be useful to name the columns from Q1 to Q_n

  columns=[]
  compteur=1
  for k in range(nb_quest):
    column_name='Q'+str(compteur)
    compteur=compteur+1
    columns.append(column_name)
    
  return columns



#Define the MatrixFacto class

class MatrixFactorization():

    def __init__(self, R, K, alpha, beta, iterations):

        """
        We will try to predict the '0' in the entry matrix using matrix factorization

        Arguments :
        - R (matrix/ndarray): user-question rating matrix
        - K (int) : number of latent features

        - alpha (float) : learning rate/rate of approaching the minimum by using gradient descent update rules when we derivate the MSE.
        Here, α is a constant whose value determines the rate of approaching the minimum. Usually we will choose a small value for α, say 0.0002. This is because if we make too large a step towards the minimum we may run into the risk of missing the minimum and end up oscillating around the minimum.


        - beta (float)  : regularization parameter, introduce regularization to avoid overfitting.
        In other words, the new parameter β is used to control the magnitudes of the user-feature and item-feature vectors such that P and Q would give a good approximation of R without having to contain large numbers. 
        In practice, β is set to some values in the order of 0.02.
        """

        self.R = R
        self.num_users, self.num_quests = R.shape
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iterations = iterations


    def train(self):

        #Initialize user and item latent feature matrice P and Q with a normal distribution.

        #Maybe, we could after choose the mean and the standard deviation of the normal distribution to reduce the complexity 
        #numpy.random.normal(loc=0.0, scale=1.0, size=None)

        self.P = np.random.normal(size=(self.num_users, self.K))
        self.Q = np.random.normal(size=(self.num_quests, self.K))


        # Initialize the biases
        #For example, we can assume that when a rating is generated, some biases may also contribute to the ratings. 
        #In particular, every user may have his or her own bias, meaning that he or she may tend to rate items higher or lower than the others.

        # b_u represent the bias of the user u
        # b_i represent the bias of the item i
        #b represent the global bias, which is the mean of all ratings

        self.b_u = np.zeros(self.num_users)
        self.b_i = np.zeros(self.num_quests)

        #Only take the mean where R[i][j]!=0 because 0 means that the values needs to be predicted.

        self.b = np.mean(self.R[np.where(self.R != 0)])


        # Create a list of training samples
        
        self.training_samples = []

        for i in range(self.num_users):
          for j in range(self.num_quests):
            if self.R[i][j]!=0:
              self.training_samples.append((i,j,self.R[i][j]))

        
        # Ggradient descent for number of iterations

        training_process = []

        for i in range(self.iterations):

            #We just randomly reorganize the training_samples
            #For exemple, if we have A=np.arange(10), np.random.shuffle(A)=[1 7 5 2 9 4 3 6 0 8]
            np.random.shuffle(self.training_samples)
            
            #We apply the gradient descent to different training samples, and we will take the better one
            self.stochastic_gradient_descent()
            
            #Then, we compute the MSE
            mse = self.mse()


            training_process.append((i, mse))

            if(i%100==0):
              print("Iteration: %d ; error = %.4f" % (i, mse))

        return training_process

    def mse(self):
        
        #A function to compute the total mean square error between the predicted matrice and the 'original' one.
        
        rows, col = self.R.shape
        predicted = self.predicted_matrice()
        error = 0

        for i in range(rows):
          for j in range(col):
            if self.R[i][j]!=0:
              error += pow(self.R[i][j] - predicted[i][j], 2)

        return np.sqrt(error)

    def stochastic_gradient_descent(self):
        
        #Perform stochastic graident descent
        
        for i, j, score in self.training_samples:
            # Computer prediction and error

            prediction = self.get_rating(i, j)
            error = (score - prediction)

            # Update biases, see formula up there
            self.b_u[i] += self.alpha * (error - self.beta * self.b_u[i])
            self.b_i[j] += self.alpha * (error - self.beta * self.b_i[j])


            # Update user and item latent feature matrices, formula up there too
            self.P[i, :] += self.alpha * (error * self.Q[j, :] - self.beta * self.P[i,:])
            self.Q[j, :] += self.alpha * (error * self.P[i, :] - self.beta * self.Q[j,:])

    def get_rating(self, i, j):
        
        # Get the predicted rating of user i and question j
        # .dot is to multiply matrice
        # .T is the transpose matrice
        
        prediction = self.b + self.b_u[i] + self.b_i[j] + self.P[i, :].dot(self.Q[j, :].T)

        return prediction

    def predicted_matrice(self):
        
        #Computer the full matrix
        
        return self.b + self.b_u[:,np.newaxis] + self.b_i[np.newaxis:,] + self.P.dot(self.Q.T)





#This is how to call the class and train the model

#Create the model

"""
    - user_item_matrix is a np.array (matrix) of size number_of_user*number_of_item.
    - K is the number of latent features, the more there is the most personalized the model will be.
"""

#Here, we will just create the USER_ITEM_MATRIX to test our code

nb_quest=20
nb_users=100

#Generate the columns "Q_1" to "Q_n"
columns=generate_columns_name(nb_quest)

#Generate the matrix
user_item_matrix=np.array(generate_user_item_matrix(nb_quest, nb_users))

#Create a new instance of our model
model = MatrixFactorization(user_item_matrix, K=3, alpha=0.01, beta=0.01, iterations=1001)

#Train the model
training_process = model.train()

print()
print("Global bias:")
print(model.b)
print()
print("User bias:")
print(model.b_u)
print()
print("Question bias:")
print(model.b_i)
print()

print("Predicted matrice :")
predicted_matrice=model.predicted_matrice()




#df_predicted_matrice=pd.DataFrame(model.predicted_matrice(), columns=generate_columns_name(nb_quest))
#df_predicted_matrice.round()

# Parameters on the weight algo
# question difficulty
# correct answer
# feedback (1 à 4)







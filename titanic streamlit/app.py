import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from uploaded file
def load_data(file):
    df = pd.read_csv(file)
    return df

# Preprocess data
def preprocess_data(df):
    # Handle missing values
    df = df.fillna(method='ffill')  # Fills missing values with previous values
    return df

# Display histograms and pie charts
def display_data_visualizations(train_data, test_data):
    st.subheader('Data Visualizations')
    
    # Histogram for Age distribution
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].set_title('Age Distribution - Training Data')
    sns.histplot(train_data['Age'], bins=20, ax=ax[0])
    
    ax[1].set_title('Age Distribution - Test Data')
    sns.histplot(test_data['Age'], bins=20, ax=ax[1])
    
    st.pyplot(fig)
    
    # Pie chart for Survival rate
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].set_title('Survival Rate - Training Data')
    train_data['Survived'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax[0], labels=['Not Survived', 'Survived'])
    
    ax[1].set_title('Survival Rate - Test Data')
    test_data_fake = test_data.copy()
    test_data_fake['Survived'] = 0  # Creating fake survival data for test data visualization
    test_data_fake['Survived'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax[1], labels=['Not Survived', 'Survived'])
    
    st.pyplot(fig)


# Preprocess data
def preprocess_data(df):
    # Handle missing values
    df = df.fillna(method='ffill')  # Fills missing values with previous values
    
    # Encode categorical variables
    label_encoders = {}
    for column in df.select_dtypes(include='object').columns:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le
    
    return df, label_encoders

# Train decision tree model
def train_model(df):
    X = df.drop(['Survived', 'Name', 'Ticket', 'Cabin', 'Embarked'], axis=1)
    y = df['Survived']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Calculate accuracy on test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return model, accuracy

# Display decision tree
def display_tree(model, X):
    st.set_option('deprecation.showPyplotGlobalUse', False)  # Prevents a warning
    plt.figure(figsize=(20, 10))
    plot_tree(model, filled=True, feature_names=X.columns, class_names=['Not Survived', 'Survived'])
    st.pyplot()

def main():
    st.title('Titanic Survival Prediction')
    
    # File upload for training data
    st.subheader('Upload Training Data (CSV file)')
    train_file = st.file_uploader('Upload CSV', type=['csv'])
    if train_file is not None:
        train_data = load_data(train_file)
        st.write(train_data.head())
        
        # Preprocess data
        processed_data, _ = preprocess_data(train_data)
        
        # Train model
        model, accuracy = train_model(processed_data)
        
        # Display decision tree
        st.subheader('Decision Tree Visualization')
        display_tree(model, processed_data.drop(['Survived', 'Name', 'Ticket', 'Cabin', 'Embarked'], axis=1))
        
        # Explanation of results
        st.subheader('Interpreting Decision Tree Results')
        st.markdown("""
        A decision tree model has been trained using the provided data.
        
        **Accuracy on test set:** {:.2f}%
        
        When using the decision tree for prediction:
        - The model makes decisions based on the values of features (e.g., Age, Sex, Pclass).
        - It navigates through the tree structure using these features to predict whether a passenger survived or not.
        - The confidence level or certainty of each prediction can be influenced by various factors including the depth of the tree and the purity of the nodes.
        
        The visualization above shows how the decision tree makes decisions based on the features in the dataset.
        """.format(accuracy * 100))

if __name__ == '__main__':
    main()

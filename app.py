import streamlit as st
from owlready2 import *
import sqlite3
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches 

import streamlit as st
from owlready2 import *
import os

# --- Load and Validate the Ontology ---
ONTOLOGY_PATH = os.path.abspath("ShapeOntology.owx")  

if not os.path.exists(ONTOLOGY_PATH):
    st.error("Ontology file 'ShapeOntology.owx' not found. Please ensure it's in the same directory.")
else:
    try:
        # Load the ontology
        onto = get_ontology(f"file://{ONTOLOGY_PATH}").load()
        
        # Expected classes in the ontology
        expected_classes = ["Triangle", "Square", "Circle", "Rectangle", "Parallelogram", "Trapezoid", "Ellipse"]
        
        # Validate the existence of the expected classes
        missing_classes = [cls for cls in expected_classes if not getattr(onto, cls, None)]
        
        if missing_classes:
            st.error(f"Missing classes in the ontology: {', '.join(missing_classes)}")
        else:
            st.success("Ontology loaded successfully, and all expected classes are present!")
    
    except Exception as e:
        st.error(f"Error loading the ontology: {e}")


# --- Database Setup ---
conn = sqlite3.connect('user_progress.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS progress (
    username TEXT,
    shape TEXT,
    correct_attempts INTEGER,
    incorrect_attempts INTEGER
)
''')
conn.commit()

# --- Function to Calculate Area ---
def calculate_area(shape, dimensions):
    try:
        if shape == "Triangle":
            base = float(dimensions['base'])
            height = float(dimensions['height'])
            area = 0.5 * base * height
        elif shape == "Square":
            side = float(dimensions['side'])
            area = side ** 2
        elif shape == "Circle":
            radius = float(dimensions['radius'])
            area = 3.14 * radius ** 2
        elif shape == "Rectangle":
            length = float(dimensions['length'])
            width = float(dimensions['width'])
            area = length * width
        elif shape == "Parallelogram":
            base = float(dimensions['base'])
            height = float(dimensions['height'])
            area = base * height
        elif shape == "Trapezoid":
            base1 = float(dimensions['base1'])
            base2 = float(dimensions['base2'])
            height = float(dimensions['height'])
            area = 0.5 * (base1 + base2) * height
        elif shape == "Ellipse":
            major_axis = float(dimensions['major_axis'])
            minor_axis = float(dimensions['minor_axis'])
            area = 3.14 * major_axis * minor_axis
        else:
            return None, "Invalid shape selected"
        return area, None
    except ValueError:
        return None, "Invalid input. Please enter numerical values."

# --- Function to Record Progress ---
def record_progress(username, shape, correct=True):
    cursor.execute('SELECT * FROM progress WHERE username = ? AND shape = ?', (username, shape))
    record = cursor.fetchone()
    if record:
        correct_attempts = record[2] + (1 if correct else 0)
        incorrect_attempts = record[3] + (0 if correct else 1)
        cursor.execute('''
            UPDATE progress
            SET correct_attempts = ?, incorrect_attempts = ?
            WHERE username = ? AND shape = ?
        ''', (correct_attempts, incorrect_attempts, username, shape))
    else:
        cursor.execute('''
            INSERT INTO progress (username, shape, correct_attempts, incorrect_attempts)
            VALUES (?, ?, ?, ?)
        ''', (username, shape, 1 if correct else 0, 0 if correct else 1))
    conn.commit()

# --- Function to Provide Hints ---
def provide_hint(shape):
    hints = {
        "Triangle": "Hint: The area of a triangle is 0.5 × base × height.",
        "Square": "Hint: The area of a square is side × side.",
        "Circle": "Hint: The area of a circle is π × radius².",
        "Rectangle": "Hint: The area of a rectangle is length × width.",
        "Parallelogram": "Hint: The area of a parallelogram is base × height.",
        "Trapezoid": "Hint: The area of a trapezoid is 0.5 × (base1 + base2) × height.",
        "Ellipse": "Hint: The area of an ellipse is π × major axis × minor axis."
    }
    return hints.get(shape, "No hint available for this shape.")

# --- Function to Visualize Shapes ---
def visualize_shape(shape, dimensions):
    plt.figure()
    ax = plt.gca()
    try:
        if shape == "Triangle":
            base = float(dimensions['base'])
            height = float(dimensions['height'])
            plt.plot([0, base, base / 2, 0], [0, 0, height, 0], 'b-')
            plt.fill([0, base, base / 2, 0], [0, 0, height, 0], alpha=0.3)
        elif shape == "Square":
            side = float(dimensions['side'])
            ax.add_patch(patches.Rectangle((0, 0), side, side, fill=True, alpha=0.3))
        elif shape == "Circle":
            radius = float(dimensions['radius'])
            circle = patches.Circle((0, 0), radius, fill=True, alpha=0.3)
            ax.add_patch(circle)
            ax.set_xlim(-radius-1, radius+1)
            ax.set_ylim(-radius-1, radius+1)
        elif shape == "Rectangle":
            length = float(dimensions['length'])
            width = float(dimensions['width'])
            ax.add_patch(patches.Rectangle((0, 0), length, width, fill=True, alpha=0.3))
        elif shape == "Parallelogram":
            base = float(dimensions['base'])
            height = float(dimensions['height'])
            plt.plot([0, base, base + height, height, 0], [0, 0, height, height, 0], 'b-')
        elif shape == "Trapezoid":
            base1 = float(dimensions['base1'])
            base2 = float(dimensions['base2'])
            height = float(dimensions['height'])
            plt.plot([0, base1, base1 - ((base1 - base2) / 2), -((base1 - base2) / 2), 0], [0, 0, height, height, 0], 'b-')
        elif shape == "Ellipse":
            major_axis = float(dimensions['major_axis'])
            minor_axis = float(dimensions['minor_axis'])
            ellipse = patches.Ellipse((0, 0), 2 * major_axis, 2 * minor_axis, fill=True, alpha=0.3)
            ax.add_patch(ellipse)
            ax.set_xlim(-major_axis - 1, major_axis + 1)
            ax.set_ylim(-minor_axis - 1, minor_axis + 1)
        ax.set_aspect('equal', adjustable='box')
        st.pyplot(plt)
    except ValueError:
        st.error("Invalid dimensions provided for visualization.")

# --- Streamlit UI ---
st.title("AI-Powered Intelligent Tutoring System for Geometric Shapes")

# User input for username
username = st.text_input("Enter your name:")

# Shape selection
shape = st.selectbox("Select a shape:", ["Triangle", "Square", "Circle", "Rectangle", "Parallelogram", "Trapezoid", "Ellipse"])

# Dynamic input fields based on shape selection
dimensions = {}
if shape == "Triangle":
    dimensions['base'] = st.text_input("Enter base of the triangle:")
    dimensions['height'] = st.text_input("Enter height of the triangle:")
elif shape == "Square":
    dimensions['side'] = st.text_input("Enter side length of the square:")
elif shape == "Circle":
    dimensions['radius'] = st.text_input("Enter radius of the circle:")
elif shape == "Rectangle":
    dimensions['length'] = st.text_input("Enter length of the rectangle:")
    dimensions['width'] = st.text_input("Enter width of the rectangle:")
elif shape == "Parallelogram":
    dimensions['base'] = st.text_input("Enter base of the parallelogram:")
    dimensions['height'] = st.text_input("Enter height of the parallelogram:")
elif shape == "Trapezoid":
    dimensions['base1'] = st.text_input("Enter first base of the trapezoid:")
    dimensions['base2'] = st.text_input("Enter second base of the trapezoid:")
    dimensions['height'] = st.text_input("Enter height of the trapezoid:")
elif shape == "Ellipse":
    dimensions['major_axis'] = st.text_input("Enter major axis of the ellipse:")
    dimensions['minor_axis'] = st.text_input("Enter minor axis of the ellipse:")

# User-provided area for verification
user_area = st.text_input("Enter your calculated area (numerical value):")

# Calculate button
if st.button("Check Answer"):
    if username:
        correct_area, error = calculate_area(shape, dimensions)
        if error:
            st.error(error)
            st.info(provide_hint(shape))
        else:
            try:
                user_area_value = float(user_area)
                if abs(user_area_value - correct_area) < 0.01:
                    st.success(f"Correct! The area of the {shape} is: {correct_area:.2f}")
                    record_progress(username, shape, correct=True)
                else:
                    st.error(f"Incorrect. The correct area of the {shape} is: {correct_area:.2f}")
                    st.info(provide_hint(shape))
                    record_progress(username, shape, correct=False)
                visualize_shape(shape, dimensions)
            except ValueError:
                st.error("Invalid input for area. Please enter a numerical value.")
    else:
        st.error("Please enter your name.")

# Show progress
if st.button("Show Progress"):
    if username:
        cursor.execute('SELECT * FROM progress WHERE username = ?', (username,))
        records = cursor.fetchall()
        if records:
            st.write("Your Progress:")
            for record in records:
                st.write(f"Shape: {record[1]}, Correct Attempts: {record[2]}, Incorrect Attempts: {record[3]}")
        else:
            st.write("No progress recorded yet.")
    else:
        st.error("Please enter your name to see progress.")

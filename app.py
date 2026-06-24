from flask import Flask, render_template_string, request

app = Flask(__name__)

# A simple HTML interface embedded directly in the code
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Calculator</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        input, select, button { padding: 10px; font-size: 16px; margin: 5px; }
    </style>
</head>
<body>
    <h2>Simple Flask Calculator</h2>
    <form method="POST">
        <input type="number" step="any" name="num1" required value="{{ num1 }}">
        <select name="operation">
            <option value="add" {% if op == 'add' %}selected{% endif %}>+</option>
            <option value="subtract" {% if op == 'subtract' %}selected{% endif %}>-</option>
            <option value="multiply" {% if op == 'multiply' %}selected{% endif %}>*</option>
            <option value="divide" {% if op == 'divide' %}selected{% endif %}>/</option>
        </select>
        <input type="number" step="any" name="num2" required value="{{ num2 }}">
        <button type="submit">=</button>
    </form>
    
    {% if result is not none %}
        <h3>Result: {{ result }}</h3>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def calculator():
    result = None
    num1 = num2 = op = ""
    
    if request.method == 'POST':
        try:
            num1 = float(request.form['num1'])
            num2 = float(request.form['num2'])
            op = request.form['operation']
            
            if op == 'add': result = num1 + num2
            elif op == 'subtract': result = num1 - num2
            elif op == 'multiply': result = num1 * num2
            elif op == 'divide': result = num1 / num2 if num2 != 0 else "Error (Div by 0)"
        except ValueError:
            result = "Invalid Input"

    return render_template_string(HTML_TEMPLATE, result=result, num1=num1, num2=num2, op=op)

if __name__ == '__main__':
    app.run(debug=True)

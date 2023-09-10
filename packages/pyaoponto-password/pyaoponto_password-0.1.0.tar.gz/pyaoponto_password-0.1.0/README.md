## :space_invader: About

This code defines a function called "gerar_senha_forte" that generates a strong password. The function takes an optional argument called "tamanho" which specifies the length of the password (default is 6 characters).

Inside the function, it first checks if the specified length is less than 6. If it is, it prints a message and returns None.

If the length is 6 or greater, it creates a string variable called "caracteres" which contains all the possible characters for the password. This includes uppercase letters, lowercase letters, digits, and punctuation.

Next, it creates an empty list called "senha" and appends one random character from each category (uppercase, lowercase, digit, punctuation) to the list.

After that, it enters a for loop that repeats for (tamanho - 4) iterations. In each iteration, it appends a random character from the "caracteres" string to the "senha" list.

Once the loop is complete, it shuffles the order of the characters in the "senha" list using a cryptographic secure random number generator.

Finally, it joins all the characters in the "senha" list into a single string and returns it as the generated strong password.

## :wrench: Requirements

The following Python libraries are required:

- secrets
- string


## :runner:  Usage

$ python .\strong_password\generator.py

This will execute the code and generate a strong password.

## :raising_hand: Contribution

All contributions are welcome! Please open an issue or submit a pull request.


# java_compiler
Programming language theory project. Java source code lexer, semantic analyzer, optimizer and code generator.

The compiler recognizes and can process the following elements of Java language:
1. Classes
2. Functions with parameters
3. Data types
	* Int
	* Boolean
4. Logical and arithmetic operations
5. Operators
	* Assignment
	* If
6. Operands
	* Variables
	* Constants (integers with base 10 or boolean)

For example, the following source code in Java:

```java
class super{
  
    class lapsha_s_sosiskami{
        void lapsh_method(int param){
            int var;
            var = param;
        }
        int alesha;
        int sosiska;
        boolean kotiki;
    }
    void function(int ape){
        boolean test, local_kek, result, kotiki;
        int a, b, c;
        kotiki = (true != (((1 * 2 + 3) % 7 - (18 / 9)) == ((((((2)))))))) == false == local_kek;
        a = 4;
        b = 2;
        function(ape);
    }


    boolean global;

    void lalala(int first_arg, boolean second_arg){

    }

    void main(int first_arg, boolean second_arg){
        boolean var, test, local_kek, result, kotiki;
        int a, b, c, global_int;
        kotiki = (true != (((1 * 2 + 3) % 7 - (18 / 9)) == ((((((2)))))))) == false == local_kek;
        a = 4;
        b = 2;    
        var = true;
        if (var && true){
            var = false;
            if (var){
                a = 7;
            }
            else{
                a = 10;
            }
        }
        else{
            var = true;
        }
        
    }

}
```

will be translated to 

```assembly
.data
        super@lapsha_s_sosiskami@alesha: dd 0
        super@lapsha_s_sosiskami@sosiska: dd 0
        super@lapsha_s_sosiskami@kotiki: db 0
        super@global: db 0
.text
        global _main
_lapsh_method
        push ebp                    ;prolog
        mov ebp, esp
        sub esp, 4
        push ebx
        push esi
        push edi
        mov eax, [-4]
        mov [0], eax
        pop edi                     ;epilog
        pop esi
        pop ebx
        mov esp, ebp
        pop ebp
        ret
_function
        push ebp                    ;prolog
        mov ebp, esp
        sub esp, 16
        push ebx
        push esi
        push edi
        mov eax, 2
        mov ecx, 1
        mul ecx
        mov ebx, eax
        mov eax, 3
        add eax, ebx
        mov ebx, eax
        xor edx, edx
        mov eax, 7
        mov ecx, ebx
        div ecx
        mov ebx, edx
        xor edx, edx
        mov eax, 9
        mov ecx, 18
        div ecx
        mov ebx, eax
        mov eax, ebx
        sub eax, ebx
        mov ebx, eax
        mov eax, ebx
        mov [3], eax
        mov eax, 4
        mov [4], eax
        mov eax, 2
        mov [8], eax
        mov eax, 2
        mov ecx, 1
        mul ecx
        mov ebx, eax
        mov eax, 3
        add eax, ebx
        mov ebx, eax
        xor edx, edx
        mov eax, 7
        mov ecx, ebx
        div ecx
        mov ebx, edx
        xor edx, edx
        mov eax, 9
        mov ecx, 18
        div ecx
        mov ebx, eax
        mov eax, ebx
        sub eax, ebx
        mov ebx, eax
        mov eax, ebx
        mov [3], eax
        mov eax, 4
        mov [4], eax
        mov eax, 2
        mov [8], eax
        mov eax, 2
        mov ecx, 1
        mul ecx
        mov ebx, eax
        mov eax, 3
        add eax, ebx
        mov ebx, eax
        xor edx, edx
        mov eax, 7
        mov ecx, ebx
        div ecx
        mov ebx, edx
        xor edx, edx
        mov eax, 9
        mov ecx, 18
        div ecx
        mov ebx, eax
        mov eax, ebx
        sub eax, ebx
        mov ebx, eax
        mov eax, ebx
        mov [3], eax
        mov eax, 4
        mov [4], eax
        mov eax, 2
        mov [8], eax
        mov eax, 2
        mov ecx, 1
        mul ecx
        mov ebx, eax
        mov eax, 3
        add eax, ebx
        mov ebx, eax
        xor edx, edx
        mov eax, 7
        mov ecx, ebx
        div ecx
        mov ebx, edx
        xor edx, edx
        mov eax, 9
        mov ecx, 18
        div ecx
        mov ebx, eax
        mov eax, ebx
        sub eax, ebx
        mov ebx, eax
        mov eax, ebx
        mov [3], eax
        mov eax, 4
        mov [4], eax
        mov eax, 2
        mov [8], eax
        mov eax, 2
        mov ecx, 1
        mul ecx
        mov ebx, eax
        mov eax, 3
        add eax, ebx
        mov ebx, eax
        xor edx, edx
        mov eax, 7
        mov ecx, ebx
        div ecx
        mov ebx, edx
        xor edx, edx
        mov eax, 9
        mov ecx, 18
        div ecx
        mov ebx, eax
        mov eax, ebx
        sub eax, ebx
        mov ebx, eax
        mov eax, ebx
        mov [3], eax
        mov eax, 4
        mov [4], eax
        mov eax, 2
        mov [8], eax
        mov eax, 2
        mov ecx, 1
        mul ecx
        mov ebx, eax
        mov eax, 3
        add eax, ebx
        mov ebx, eax
        xor edx, edx
        mov eax, 7
        mov ecx, ebx
        div ecx
        mov ebx, edx
        xor edx, edx
        mov eax, 9
        mov ecx, 18
        div ecx
        mov ebx, eax
        mov eax, ebx
        sub eax, ebx
        mov ebx, eax
        mov eax, ebx
        mov [3], eax
        mov eax, 4
        mov [4], eax
        mov eax, 2
        mov [8], eax
        push [-4]
        call function
        add esp, 4
        pop edi                     ;epilog
        pop esi
        pop ebx
        mov esp, ebp
        pop ebp
        ret
_lalala
        push ebp                    ;prolog
        mov ebp, esp
        push ebx
        push esi
        push edi
        pop edi                     ;epilog
        pop esi
        pop ebx
        mov esp, ebp
        pop ebp
        ret
_main
        push ebp                    ;prolog
        mov ebp, esp
        sub esp, 21
        push ebx
        push esi
        push edi
        mov eax, 2
        mov ecx, 1
        mul ecx
        mov ebx, eax
        mov eax, 3
        add eax, ebx
        mov ebx, eax
        xor edx, edx
        mov eax, 7
        mov ecx, ebx
        div ecx
        mov ebx, edx
        xor edx, edx
        mov eax, 9
        mov ecx, 18
        div ecx
        mov ebx, eax
        mov eax, ebx
        sub eax, ebx
        mov ebx, eax
        mov eax, ebx
        mov [4], eax
        mov eax, 4
        mov [5], eax
        mov eax, 2
        mov [9], eax
        mov eax, 1
        mov [0], eax
        mov eax, 1
        and eax, [0]
        mov ebx, eax
        mov eax, 0
        mov [0], eax
        mov eax, 7
        mov [5], eax
        mov eax, 10
        mov [5], eax
        mov eax, 1
        mov [0], eax
        pop edi                     ;epilog
        pop esi
        pop ebx
        mov esp, ebp
        pop ebp
        ret
```

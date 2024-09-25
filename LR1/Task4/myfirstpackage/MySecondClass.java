
package myfirstpackage;

public class MySecondClass{
	private int a;
	private int b;
	public MySecondClass(){
	a = 0; 
	b = 0;
	}
	public MySecondClass(int A, int B)	{
	a = A; 
	b = B;
	}
	public int getA(){
		return a;
	}
	public void setA(int A){
		a = A;
	}
	public int getB(){
		return b;
	}
	
	public void setB(int B){
		b = B;
	}
	public int operation1(){ return a+b;}

	
}
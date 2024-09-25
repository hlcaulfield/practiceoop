class MyFirstClass {
	public static void main(String[] args) {
		MySecondClass o = new MySecondClass();
		System.out.println(o.operation1());
		for (int i = 1; i <= 8; i++) {
			for (int j = 1; j <= 8; j++) {
				o.setA(i);
				o.setB(j);
				System.out.print(o.operation1());
				System.out.print(" ");
			}
		System.out.println();
		}
	}
}

class MySecondClass{
	private int a;
	private int b;
	MySecondClass(){
	a = 0; 
	b = 0;
	}
	MySecondClass(int A, int B)	{
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
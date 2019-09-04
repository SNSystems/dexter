// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -glldb" -- %S
// Radar 8775834

class A
{
public:
    A (int i=0);
    A (const A& rhs);
    const A&
    operator= (const A& rhs);
    virtual ~A() {}

    int get_int();

protected:
    int m_int;
};

A::A (int i) :
    m_int(i)
{
}

A::A (const A& rhs) :
    m_int (rhs.m_int)
{
}

const A &
A::operator =(const A& rhs)
{
    m_int = rhs.m_int;
    return *this;
}

int A::get_int()
{
    return m_int;
}

class B
{
public:
    B () {}

    A AInstance();
};

A
B::AInstance()
{
    A a(12);
    return a;
} // DexLabel('ret')

int main (int argc, char const *argv[])
{
    B b;
    int return_val = b.AInstance().get_int();

    A a(b.AInstance());
    return return_val;
}

// LLDB does not print artificial members.
// DexExpectWatchValue('a.m_int', '12', on_line='ret')


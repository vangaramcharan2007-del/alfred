#include <iostream>
#include <string>

// Encapsulation: Grouping data and methods that operate on them within a class.
// Data hiding is achieved by making member variables private.
class Entity {
private:
    std::string id;

protected:
    std::string name;

public:
    Entity(std::string n, std::string i) : name(n), id(i) {}
    virtual ~Entity() {} // Virtual destructor for safe polymorphic deletion

    // Pure virtual function making this class abstract
    virtual void executeProtocol() const = 0;

    std::string getID() const {
        return id;
    }
};

// Inheritance: Subclasses inherit protected/public attributes from the base class.
class Agent : public Entity {
private:
    int clearanceLevel;

public:
    Agent(std::string n, std::string i, int cl) : Entity(n, i), clearanceLevel(cl) {}

    // Polymorphism: Overriding the base class method.
    void executeProtocol() const override {
        std::cout << "Agent " << name << " [ID: " << getID() << "] executing protocol with clearance " << clearanceLevel << ".\n";
    }
};

class Supervisor : public Entity {
public:
    Supervisor(std::string n, std::string i) : Entity(n, i) {}

    void executeProtocol() const override {
        std::cout << "Supervisor " << name << " [ID: " << getID() << "] overriding protocols for global execution.\n";
    }
};

int main() {
    std::cout << "--- Genesis Omega OOP Matrix ---\n";

    // Polymorphism in action: Using base class pointers to refer to derived class objects.
    Entity* devAgent = new Agent("Dev_Agent", "AGE-001", 3);
    Entity* ouroboros = new Supervisor("Ouroboros_Daemon", "SUP-999");

    devAgent->executeProtocol();
    ouroboros->executeProtocol();

    delete devAgent;
    delete ouroboros;

    return 0;
}

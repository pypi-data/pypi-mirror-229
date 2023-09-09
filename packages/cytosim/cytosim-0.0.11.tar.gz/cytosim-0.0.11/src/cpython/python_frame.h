#ifndef PYTHON_FRAME_H
#define PYTHON_FRAME_H

#include <fstream>
#include <sstream>
#include "sim_thread.h"
#include "stream_func.h"
//#include "frame_reader.h"
#include "iowrapper.h"
#include "glossary.h"
#include "messages.h"
#include "organizer.h"
//#include "parser.h"
//#include "simul.h"
#include "simul_prop.h"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "python_utilities.h"
namespace py = pybind11;

class Simul;
class SimulProp;
class Organizer;

void void_callback(void) {};


class PythonParser : public Parser
{
public:
        
    /// construct a Parser with given permissions
    PythonParser(Simul& simul) :Parser(simul,  0, 1, 0, 0, 0) {
        // Has not been loaded yet
        is_loaded = 0;
        // Has not been saved yet
        is_saved = 0;
        // Creating a SimThread, maybe
        sim = &simul;
    }

    /// activates the parser (from existing sim)
    void activate(std::string & input, SimThread * existing_thread) {
        thread = existing_thread;
        //thread->start();
        reader.openFile(input);
        is_loaded = 1;
    }

    /// activates the parser (from existing sim)
    void activate(std::string & input) {
        thread = new SimThread(*sim, &void_callback);
        //thread->start();
        reader.openFile(input);
        is_loaded = 1;
    }
    
    /// activates the parser (new sim)
    void activate(SimThread * existing_thread) {
        Parser::readConfig();
        thread = existing_thread;
        thread->start();
        is_loaded = 2;
    }
    
    /// activates the parser (new sim)
    void activate() {
        Parser::readConfig();
        thread = new SimThread(*sim, &void_callback);
        thread->start();
        is_loaded = 2;
    }
    
    /// A framereader
    FrameReader reader;
    
    /// Check if simulation is loaded
    int is_loaded ;
    
    /// A thread
    SimThread * thread;
    
    /// Has the simulation been saved 
    bool is_saved ;
    
    /// is the simulation
    Simul * sim;
    
    /// Loads the simulation at a given time
    int load(int fr) {
        int loader = 1;
        if (is_loaded == 1) {
            try 
            {
                //loader = thread->loadFrame(fr);
                loader = reader.loadFrame(*sim,fr);
                if (loader!=0) {
                    std::clog << "Unable to load frame " << fr << ". Maybe frame does not exist." << std::endl;
                } 
                    
            }
            catch( Exception & e )
            {
                std::clog << "Aborted: " << e.what() << '\n';
            }
        }
        else{
            std::clog << "Simulation not loaded : use cytosim.open() first" << std::endl;
        }
        
        return loader;
    }
    
    int next() {
        return reader.loadNextFrame(*sim);
    }
};

/// ObjGroup : a vector of objects of same type having the same property
template<typename Obj, typename Prp> 
class ObjGroup : public std::vector<Obj*>{
    public:
    Prp * prop;
    ObjGroup() = default;
    ObjGroup(Prp * p) : ObjGroup() {prop = p ;};
    ~ObjGroup() = default;
};

/// ObjMap : a map <string, ObjGroup>
template<typename Obj, typename Prp> 
using ObjMap = std::map<std::string,ObjGroup<Obj,Prp>> ;

/// ObjVec : a vec <Obj*>
template<typename Obj> 
using ObjVec = std::vector<Obj*> ;

/// Distribute the objects (pointers) in the groups and in the dict.
template<typename Obj, typename Prp, typename Set> 
void distribute_objects(Simul * sim, py::dict & objects, ObjMap<Obj,Prp> mappe, Set & set, std::string categ ) {
    // First we list all objects in category, and create the ObjGroups in the map
    PropertyList plist = sim->properties.find_all(categ);
    if (!plist.empty()) {
        for ( Property * i : plist )
            {
                Prp * fp = static_cast<Prp*>(i);
                mappe[fp->name()] = ObjGroup<Obj,Prp>(fp);
            }
        // Then we assign all objects to their groups
        Obj * obj = set.first();
        while (obj) {
            mappe[obj->property()->name()].push_back(obj);
            obj = obj->next();
        }
        // Then we fill the dictionnary
        for (const auto &[name, group] : mappe) {
            objects[py::cast(name)] = group;
        }
        
    }
}
 
/// Distribute the objects (pointers) in the groups and in the dict ; 
// special case for couple, single, where firstID needs to be used
template<typename Obj, typename Prp, typename Set> 
void distribute_objects_wID(Simul * sim, py::dict & objects, ObjMap<Obj,Prp> mappe, Set & set, std::string categ )
{
    // First we list all objects in category, and create the ObjGroups in the map
    PropertyList plist = sim->properties.find_all(categ);
    if (!plist.empty()) {
        for ( Property * i : plist )
            {
                Prp * fp = static_cast<Prp*>(i);
                mappe[fp->name()] = ObjGroup<Obj,Prp>(fp);
            }
        // Then we assign all objects to their groups
        // (OUTDATED) We need to add a static cast here because ...
        //      sometimes first, last comme from the base class ObjectSet, 
        //      sometimes from a derived class, e.g. FiberSet
        //      but at least we are not touching the simulation files :)
        Obj* obj = set.firstID();
        while (obj) 
       {
            mappe[obj->property()->name()].push_back(obj);
            obj = set.nextID(obj);
        }
        // Then we fill the dictionnary
        for (const auto &[name, group] : mappe) {
            objects[py::cast(name)] = group;
        }
        
    }
}

/// declare_group() : creates a python interface for an ObjGroup
/// Unused for now, but should be used to benefit of pybind11's stl containers interface
template<typename Group, typename Obj>
auto declare_group(py::module &mod, Group group, std::vector<Obj*> gg , std::string name) { 
        py::class_<std::vector<Obj*>  >(mod, ("Vector"+name).c_str(), 
                    "Behaves as a list of objects ");
        return py::class_<Group, std::vector<Obj*>  >(mod, (name+"Group").c_str(),
                    "Behaves as a list of objects with the same properties")
            .def_readwrite("prop",   &Group::prop , py::return_value_policy::reference);
}

/// declare_group() : creates a python interface for an ObjGroup
template<typename Group>
auto declare_group(py::module &mod, Group group, std::string name) { 
        return py::class_<Group>(mod, name.c_str(),  "Behaves as a list of objects with the same properties")
            .def("__len__", [](const Group &v) { return v.size(); })
            .def("size", &Group::size)
            .def_readwrite("prop",   &Group::prop , py::return_value_policy::reference)
            .def("__iter__", [](Group &v) {
                return py::make_iterator(v.begin(), v.end());
            }, py::keep_alive<0, 1>())
            .def("__getitem__",[](const Group &v, size_t i) {
                int s = v.size();
                if (i<0) {i+=s;} // Python time negative indexing
				if (i >= s or i<0) {
                         throw py::index_error();
                     }
                     return v[i];
                 }, py::return_value_policy::reference);
}


/// A time frame ; basically a wrapper around a object dictionnary
// This would need to be better done
class Frame 
{
public:
        /// An Objectmap is map of  (string,objectgroup)
        ObjMap<Fiber,FiberProp> fibers;
        ObjMap<Solid,SolidProp> solids;
        ObjMap<Bead,BeadProp> beads;
        ObjMap<Sphere,SphereProp> spheres;
        ObjMap<Organizer,Property> organs;
        ObjMap<Space,SpaceProp> spaces;
        ObjMap<Couple,CoupleProp> couples;
        ObjMap<Single,SingleProp> singles;

        // Time of the frame
        real time;
        int index;
        int loaded;
        
        /// pointer to simul
        Simul * simul;
        
        /// pointer to parser
        //PythonParser * parser;
        
        /// The party zone
        py::dict objects;
        
        /// Default constr and destrc
        Frame(PythonParser & pyParse) {
            //parser = &pyParse;
            simul = pyParse.sim;
            update();
        }
        
        /// Default constr and destrc
        Frame(Simul * sim) {
            simul = sim;
            update();
        }
        
        
        void load(int t) {
            
        }
        void update() {
            std::vector<std::string> categories = std::vector<std::string>{"aster","nucleus","bundle","fake"};
            //extern std::vector<std::string>  categories;
            
            distribute_objects(simul,objects, fibers, simul->fibers, std::string("fiber") ) ;
            distribute_objects(simul,objects, solids, simul->solids, std::string("solid") ) ;
            distribute_objects(simul,objects, spaces, simul->spaces, std::string("space") ) ;
            distribute_objects(simul,objects, beads, simul->beads, std::string("bead") ) ;
            distribute_objects(simul,objects, spheres, simul->spheres, std::string("sphere") ) ;
            // For organizer, the we have to check the different categories
            for (auto categ : categories) {
                distribute_objects(simul,objects, organs, simul->organizers, std::string(categ) ) ;
            }
            // for couple and single we need to use firstID, nextID
            distribute_objects_wID(simul,objects, couples, simul->couples, std::string("couple") ) ;
            distribute_objects_wID(simul,objects, singles, simul->singles, std::string("single") ) ;
            
            time = simul->time();
            //current->index = frame;
            loaded = 1;
        };
        
        Frame() = default;
        ~Frame() = default;
};



#endif

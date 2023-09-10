package main

/*
#include <stdlib.h>
*/
import "C"

//export startClientFromJSON
func startClientFromJSON(json string) {
	StartFromJSON(json)
}

func main() {
	Execute()
}

#*****************************************************************************
#  Copyright (C) 2012 Jim Stark <jstarx@gmail.com>
#                2013 Simon King <simon.king@uni-jena.de>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty
#    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License for more details; the full text
#  is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.factory import UniqueFactory
from sage.structure.parent import Parent

class QuiverHomSpaceFactory(UniqueFactory):
    """
    A homomorphism of quiver representations is for each vertex of the quiver a
    homomorphism of the spaces assigned to those vertices such that these
    homomorphisms commute with the edge maps.  This class handles the set of all
    such maps, Hom_Q(M, N).

    INPUT:

    - ``domain`` - QuiverRep, the domain of the homomorphism space

    - ``codomain`` - QuiverRep, the codomain of the homomorphism space

    OUTPUT:

    - QuiverHomSpace, the homomorphism space Hom_Q(domain, codomain)

    .. NOTES::

        The quivers of the domain and codomain must be equal or a ValueError is
        raised.

    EXAMPLES::

        sage: from sage.quivers.quiver import Quiver
        sage: from sage.quivers.homspace import QuiverHomSpace
        sage: from sage.quivers.representation import QuiverRep
        sage: Q = Quiver({1:{2:['a', 'b']}})
        sage: H = QuiverHomSpace(Q.S(QQ, 2), Q.P(QQ, 1))
        sage: H.dimension()
        2
        sage: H.gens()
        [Homomorphism of representations of Quiver on 2 vertices, Homomorphism of representations of Quiver on 2 vertices]
    """

    def create_key(self, domain, codomain):
        """
        Returns a key for the specified Hom space.

        The key is a tuple of length two, the two entries being the keys for the domain
        and codomain.

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: QuiverHomSpace.create_key(Q.P(GF(3), 1), Q.S(GF(3), 1))
            ((Finite Field of size 3, Quiver on 2 vertices, 'paths', (a, b, invalid path, e_1)), (Finite Field of size 3, Quiver on 2 vertices, 'values', Vector space of dimension 1 over Finite Field of size 3, Vector space of dimension 0 over Finite Field of size 3, [], []))
        """

        # Check that the quivers and base rings are the same
        if domain._quiver is not codomain._quiver:
            raise ValueError("The quivers of the domain and codomain must be identical.")
        if domain._base_ring is not codomain._base_ring:
            raise ValueError("The base rings of the domain and codomain must be identical.")

        # Create and return the key
        return tuple([domain._factory_data[2], codomain._factory_data[2]])

    def create_object(self, version, key, **extra_args):
        """
        Creates a QuiverHomSpace from the key.

        The key is a tuple of length two, the two entries being the keys for the domain
        and codomain.

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: key = QuiverHomSpace.create_key(Q.P(GF(3), 1), Q.S(GF(3), 1))
            sage: QuiverHomSpace.create_object(Q.version(), key)
            Dimension 1 QuiverHomSpace
        """
        from sage.quivers.representation import QuiverRep
        return QuiverHomSpace_generic(QuiverRep.get_object(version, key[0], []),
                                      QuiverRep.get_object(version, key[1], []))

QuiverHomSpace = QuiverHomSpaceFactory("QuiverHomSpace")

####################################################################################################

class QuiverHomSpace_generic(Parent):
    """
    A homomorphism of quiver representations is for each vertex of the quiver a
    homomorphism of the spaces assigned to those vertices such that these
    homomorphisms commute with the edge maps.  This class handles the set of all
    such maps, Hom_Q(M, N).

    INPUT:

    - ``domain`` - QuiverRep, the domain of the homomorphism space

    - ``codomain`` - QuiverRep, the codomain of the homomorphism space

    OUTPUT:

    - QuiverHomSpace, the homomorphism space Hom_Q(domain, codomain)

    .. NOTES::

        The quivers of the domain and codomain must be equal or a ValueError is
        raised.

    EXAMPLES::

        sage: from sage.quivers.quiver import Quiver
        sage: from sage.quivers.homspace import QuiverHomSpace
        sage: Q = Quiver({1:{2:['a', 'b']}})
        sage: H = QuiverHomSpace(Q.S(QQ, 2), Q.P(QQ, 1))
        sage: H.dimension()
        2
        sage: H.gens()
        [Homomorphism of representations of Quiver on 2 vertices, Homomorphism of representations of Quiver on 2 vertices]
    """

    ###########################################################################
    #                                                                         #
    # PRIVATE FUNCTIONS                                                       #
    #    These functions are not meant to be seen by the end user.            #
    #                                                                         #
    ###########################################################################

    def __init__(self, domain, codomain):
        """
        Type QuiverHomSpace? for more information.

        TESTS::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: H = QuiverHomSpace(Q.S(QQ, 2), Q.P(QQ, 1))
            sage: H.dimension()
            2
            sage: H.gens()
            [Homomorphism of representations of Quiver on 2 vertices, Homomorphism of representations of Quiver on 2 vertices]
        """
        # The data in the class is stored in the following private variables:
        #
        # * _base
        #      The base ring of the representations M and N.
        # * _codomain
        #      The QuiverRep object of the codomain N.
        # * _domain
        #      The QuiverRep object of the domain M.
        # * _quiver
        #      The quiver of the representations M and N.
        # * _space
        #      A free module with ambient space.
        #
        # The free module _space is the homomorphism space.  The ambient space
        # is k^n where k is the base ring and n is the sum of the dimensions of
        # the spaces of homomorphisms between the free modules attached in M
        # and N to the vertices of the quiver.  Each coordinate represents a
        # single entry in one of those matrices.

        # Get the quiver and base ring and check they they are the same for
        # both modules
        self._quiver = domain._quiver
        self._domain = domain
        self._codomain = codomain
        if self._quiver != codomain._quiver:
            raise ValueError("Representations are not over the same quiver.")
        if codomain._base_ring != domain._base_ring:
            raise ValueError("Representations are not over the same base ring.")

        # To compute the Hom Space we set up a 'generic' homomorphism where the
        # maps at each vertex are described by matrices whose entries are
        # variables.  Then the commutativity of edge diagrams gives us a
        # system of equations whose solution space is the Hom Space we're
        # looking for.  The variables will be numbered consecutively starting
        # at 0, ordered first by the vertex the matrix occurs at, then by row
        # then by column.  We'll have to keep track of which variables
        # correspond to which matrices.

        # eqs will count the number of equations in our system of equations,
        # varstart will be a list whose ith entry is the number of the variable
        # located at (0, 0) in the matrix assigned to the ith vertex.
        eqs = 0
        verts = domain._quiver.vertices()
        varstart = [0]*(len(verts) + 1)

        # First assign to varstart the dimension of the matrix assigned to the
        # previous vertex.
        for v in verts:
            varstart[verts.index(v) + 1] = domain._spaces[v].dimension()*codomain._spaces[v].dimension()
        for e in domain._quiver.edges():
            eqs += domain._spaces[e[0]].dimension()*codomain._spaces[e[1]].dimension()

        # After this cascading sum varstart[v] will be the sum of the
        # dimensions of the matrixes assigned to vertices ordered before v.
        # This is equal to the number of the first variable assigned to v.
        for i in range(2, len(varstart)):
            varstart[i] += varstart[i-1]

        # This will be the coefficient matrix for the system of equations.  We
        # start with all zeros and will fill in as we go.  We think of this
        # matrix as acting on the right so the columns correspond to equations,
        # the rows correspond to variables, and .kernel() will give a right
        # kernel as is needed.
        from sage.matrix.constructor import Matrix
        coef_mat = Matrix(codomain._base_ring, varstart[-1], eqs)

        # row keeps track of what equation we are on.  If the maps X and Y are
        # assigned to an edge e and A and B are the matrices of variables that
        # describe the generic maps between the initial and final vertices of e
        # then commutativity of the edge diagram is described by the equation
        # AY = XB, or
        #
        #          Sum_k A_ik*Y_kj - Sum_k X_ikB_kj == 0 for all i and j.
        #
        # Below we loop through these values of i,j,k and write the
        # coefficients of the equation above into the coefficient matrix.
        eqn = 0
        for e in domain._quiver.edges():
            X = domain._maps[e].matrix()
            Y = codomain._maps[e].matrix()
            for i in range(0, X.nrows()):
                for j in range(0, Y.ncols()):
                    for k in range(0, Y.nrows()):
                        coef_mat[varstart[verts.index(e[0])] + i*Y.nrows() + k, eqn] = Y[k, j]
                    for k in range(0, X.ncols()):
                        coef_mat[varstart[verts.index(e[1])] + k*Y.ncols() + j, eqn] = -X[i, k]
                    eqn += 1

        # Now we can create the hom space
        self._space = coef_mat.kernel()

        # Bind identity if domain = codomain
        if domain is codomain:
            self.identity = self._identity

        super(QuiverHomSpace_generic, self).__init__(base=codomain._base_ring,
                                                     element_constructor=self._element_constructor_)

    def _coerce_map_from_(self, other):
        """
        A coercion exists if and only if `other` is also a
        QuiverHomSpace and there is a coercion from the domain of `self`
        to the domain of `other` and from the codomain of `other` to the
        domain of `self`.

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a']}})
            sage: P = Q.P(QQ, 1)
            sage: S = Q.S(QQ, 1)
            sage: H1 = P.Hom(S)
            sage: H2 = (P/P.radical()).Hom(S)
            sage: H1.coerce_map_from(H2) # indirect doctest
            Conversion map:
                  From: Dimension 1 QuiverHomSpace
                  To:   Dimension 1 QuiverHomSpace
        """

        if not isinstance(other, QuiverHomSpace_generic):
            return False
        if not other._domain.has_coerce_map_from(self._domain):
            return False
        if not self._codomain.has_coerce_map_from(other._codomain):
            return False
        return True

    def _element_constructor_(self, data=None):
        """
        A homomorphism of quiver representations is for each vertex of the quiver a
        homomorphism of the spaces assigned to those vertices such that these
        homomorphisms commute with the edge maps.  The domain and codomain of the
        homomorphism are required to be representations over the same quiver with
        the same base ring.

        INPUT:

        - ``data`` - dict, list, QuiverRepElement or QuiverRepHom (default: empty dict)
          as follows:
          - list, data can be a list of images for the generators of the domain.  An
            error will be generated if the map so defined is not equivariant with
            respect to the action of the quiver.
          - dictionary, data can be a dictionary associating to each vertex of the
            quiver either a homomorphism with domain and codomain the spaces associated
            to this vertex in the domain and codomain modules respectively, or a matrix
            defining such a homomorphism, or an object that sage can construct such a
            matrix from.  Not all vertices must be specified, unspecified vertices are
            assigned the zero map, and keys not corresponding to vertices of the quiver
            are ignored.  An error will be generated if these maps do not commute with
            the edge maps of the domain and codomain.
          - QuiverRepElement, if the domain is a QuiverRep_with_path_basis then data
            can be a single QuiverRepElement belonging to the codomain.  The map is
            then defined by sending each path, p, in the basis to data*p.  If data is
            not an element of the codomain or the domain is not a
            QuiverRep_with_path_basis then an error will be generated.
          - QuiverRepHom, the input can also be a map ``f:D -> C`` such that there is a
            coercion from the domain of self to ``D`` and from ``C`` to the codomain of
            self.  The composition of these maps is the result.

        OUTPUT:

        - QuiverRepHom

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.representation import QuiverRep
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: from sage.quivers.representation import QuiverRepElement
            sage: Q = Quiver({1:{2:['a', 'b']}, 2:{3:['c']}})
            sage: spaces = {1: QQ^2, 2: QQ^2, 3:QQ^1}
            sage: maps = {(1, 2, 'a'): [[1, 0], [0, 0]], (1, 2, 'b'): [[0, 0], [0, 1]], (2, 3, 'c'): [[1], [1]]}
            sage: M = QuiverRep(QQ, Q, spaces, maps)
            sage: spaces2 = {2: QQ^1, 3: QQ^1}
            sage: S = QuiverRep(QQ, Q, spaces2)
            sage: H = QuiverHomSpace(S, M)

        With no additional data this creates the zero map::

            sage: f = H() # indirect doctest
            sage: f.is_zero()
            True

        We must specify maps at the vertices to get a nonzero homomorphism.  Note that
        if the dimensions of the spaces assigned to the domain and codomain of a vertex
        are equal then Sage will construct the identity matrix from ``1``::

            sage: maps2 = {2:[1, -1], 3:1}
            sage: g = H(maps2) # indirect doctest

        Here we create the same map by specifying images for the generators::

            sage: x = QuiverRepElement(M, {2: (1, -1)})
            sage: y = QuiverRepElement(M, {3: (1,)})
            sage: h = H([x, y]) # indirect doctest
            sage: g == h
            True

        If the domain is a module of type QuiverRep_with_path_basis (for example, the
        indecomposable projectives) we can create maps by specifying a single image::

            sage: Proj = Q.P(GF(7), 3)
            sage: Simp = Q.S(GF(7), 3)
            sage: im = QuiverRepElement(Simp, {3: (1,)})
            sage: H2 = QuiverHomSpace(Proj, Simp)
            sage: H2(im).is_surjective() # indirect doctest
            True
        """

        from sage.quivers.morphism import QuiverRepHom
        if data is None or data == 0:
            data = {}

        return QuiverRepHom(self._domain, self._codomain, data)

    def _repr_(self):
        """
        Default string representation.

        TESTS::

            sage: from sage.quivers.quiver import Quiver
            sage: Q = Quiver({1:{2:['a']}})
            sage: Q.P(GF(3), 2).Hom(Q.S(GF(3), 2)) # indirect doctest
            Dimension 1 QuiverHomSpace
        """

        return "Dimension " + str(self._space.dimension()) + " QuiverHomSpace"

    def __contains__(self, map):
        """
        This overloads the in operator

        TESTS::

            sage: from sage.quivers.quiver import Quiver
            sage: Q = Quiver({1:{2:['a']}})
            sage: H1 = Q.P(GF(3), 2).Hom(Q.S(GF(3), 2))
            sage: H2 = Q.P(GF(3), 2).Hom(Q.S(GF(3), 1))
            sage: H1.an_element() in H1
            True
            sage: H2.an_element() in H1
            False
        """

        from sage.quivers.morphism import QuiverRepHom
        # First check the type
        if not isinstance(map, QuiverRepHom):
            return False

        # Then check the quivers, domain, and codomain
        if self._quiver != map._quiver or self._domain != map._domain or self._codomain != map._codomain:
            return False

        # Finally check the vector
        return map._vector in self._space

    def _identity(self):
        """
        Returns the identity map.

        OUTPUT:

        - QuiverRepHom

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: Q = Quiver({1:{2:['a']}})
            sage: P = Q.P(QQ, 1)
            sage: H = P.Hom(P)
            sage: f = H.identity() # indirect doctest
            sage: f.is_isomorphism()
            True
        """

        from sage.matrix.constructor import Matrix
        from sage.quivers.morphism import QuiverRepHom
        maps = dict((v, Matrix(self._domain._spaces[v].dimension(),
                               self._domain._spaces[v].dimension(), self._base(1)))
                               for v in self._quiver)
        return QuiverRepHom(self._domain, self._codomain, maps)

    ###########################################################################
    #                                                                         #
    # ACCESS FUNCTIONS                                                        #
    #    These functions are used to view and modify the representation data. #
    #                                                                         #
    ###########################################################################

    def base_ring(self):
        """
        Returns the base ring of the representations.

        OUTPUT:

        - ring, the base ring of the representations

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: H = QuiverHomSpace(Q.S(QQ, 2), Q.P(QQ, 1))
            sage: H.base_ring()
            Rational Field
        """

        return self._base

    def quiver(self):
        """
        Returns the quiver of the representations.

        OUTPUT:

        - Quiver, the quiver of the representations

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: H = QuiverHomSpace(Q.S(QQ, 2), Q.P(QQ, 1))
            sage: H.quiver() is Q
            True
        """

        return self._quiver

    def domain(self):
        """
        Returns the domain of the hom space.

        OUTPUT:

        - QuiverRep, the domain of the Hom space

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: S = Q.S(QQ, 2)
            sage: H = QuiverHomSpace(S, Q.P(QQ, 1))
            sage: H.domain() is S
            True
        """

        return self._domain

    def codomain(self):
        """
        Returns the codomain of the hom space.

        OUTPUT:

        - QuiverRep, the codomain of the Hom space

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: P = Q.P(QQ, 1)
            sage: H = QuiverHomSpace(Q.S(QQ, 2), P)
            sage: H.codomain() is P
            True
        """

        return self._codomain

    ###########################################################################
    #                                                                         #
    # DATA FUNCTIONS                                                          #
    #    These functions return data collected from the representation.       #
    #                                                                         #
    ###########################################################################

    def dimension(self):
        """
        Returns the dimension of the hom space.

        OUTPUT:

        - integer, the dimension

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: H = QuiverHomSpace(Q.S(QQ, 2), Q.P(QQ, 1))
            sage: H.dimension()
            2
        """

        return self._space.dimension()

    def gens(self):
        """
        Returns a list of generators of the hom space

        OUTPUT:

        - list of QuiverRepHom objects, the generators

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: H = QuiverHomSpace(Q.S(QQ, 2), Q.P(QQ, 1))
            sage: H.gens()
            [Homomorphism of representations of Quiver on 2 vertices, Homomorphism of representations of Quiver on 2 vertices]
        """

        from sage.quivers.morphism import QuiverRepHom
        return [QuiverRepHom(self._domain, self._codomain, f) for f in self._space.gens()]

    def coordinates(self, hom):
        """
        Returns the coordinates of the map when expressed in terms of gens.

        INTPUT:

        - ``hom`` - QuiverRepHom

        OUTPUT:

        - list, the coordinates of the given map when written in terms of the
          generators of the QuiverHomSpace

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: S = Q.S(QQ, 2)
            sage: P = Q.P(QQ, 1)
            sage: H = QuiverHomSpace(S, P)
            sage: f = S.hom(P, {2: [[1,-1]]})
            sage: H.coordinates(f)
            [1, -1]
        """

        #Use the coordinates function on space
        return self._space.coordinates(hom._vector)

        ###########################################################################
        #                                                                         #
        # CONSTRUCTION FUNCTIONS                                                  #
        #    These functions create and return modules and homomorphisms.         #
        #                                                                         #
        ###########################################################################

    def hom(self, maps = {}):
        """
        Creates a homomorphism.

        See the QuiverRepHom documentation for more information.

        TESTS::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: from sage.quivers.representation import QuiverRepElement
            sage: Q = Quiver({1:{2:['a', 'b']}, 2:{3:['c']}})
            sage: spaces = {1: QQ^2, 2: QQ^2, 3:QQ^1}
            sage: maps = {(1, 2, 'a'): [[1, 0], [0, 0]], (1, 2, 'b'): [[0, 0], [0, 1]], (2, 3, 'c'): [[1], [1]]}
            sage: M = QuiverRep(QQ, Q, spaces, maps)
            sage: spaces2 = {2: QQ^1, 3: QQ^1}
            sage: S = QuiverRep(QQ, Q, spaces2)
            sage: H1 = QuiverHomSpace(S, M)
            sage: f = H1()
            sage: f.is_zero()
            True
            sage: maps2 = {2:[1, -1], 3:1}
            sage: g = H1(maps2)
            sage: x = QuiverRepElement(M, {2: (1, -1)})
            sage: y = QuiverRepElement(M, {3: (1,)})
            sage: h = H1([x, y])
            sage: g == h
            True
            sage: Proj = Q.P(GF(7), 3)
            sage: Simp = Q.S(GF(7), 3)
            sage: H2 = QuiverHomSpace(Proj, Simp)
            sage: im = H2({3: (1,)})
            sage: H2(im).is_surjective()
            True
        """

        from sage.quivers.morphism import QuiverRepHom
        return QuiverRepHom(self._domain, self._codomain, maps)

    def an_element(self):
        """
        Returns a homomorphism in the Hom space.

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: from sage.quivers.homspace import QuiverHomSpace
            sage: Q = Quiver({1:{2:['a', 'b']}})
            sage: S = Q.S(QQ, 2)
            sage: P = Q.P(QQ, 1)
            sage: H = QuiverHomSpace(S, P)
            sage: H.an_element() in H
            True
        """

        from sage.quivers.morphism import QuiverRepHom
        return QuiverRepHom(self._domain, self._codomain, self._space.an_element())

    def left_module(self, basis=False):
        """
        Creates the QuiverRep of self as a module over the opposite quiver.

        INPUT:

        - ``basis`` - bool, if false then only the module is returned.  If true then a
          tuple is returned.  The first element is the QuiverRep and the second element
          is a dictionary which associates to each vertex a list.  The elements of this
          list a the homomorphisms which correspond to the basis elements of that
          vertex in the module.

        OUTPUT:

        - QuiverRep or tuple

        .. WARNING::

            The codomain of the Hom space must be a left module.

        .. NOTES::

            The left action of a path e on a map f is given by (ef)(m) = ef(m).  This
            gives the Hom space its structure as a left module over the path algebra.
            This is then converted to a right module over the path algebra of the
            opposite quiver ``Q.reverse()`` and returned.

        EXAMPLES::

            sage: from sage.quivers.quiver import Quiver
            sage: Q = Quiver({1:{2:['a', 'b'], 3: ['c', 'd']}, 2:{3:['e']}})
            sage: P = Q.P(GF(3), 3)
            sage: A = Q.free_module(GF(3))
            sage: H = P.Hom(A)
            sage: H.dimension()
            6
            sage: M, basis_dict = H.left_module(true)
            sage: M.dimension_vector()
            (4, 1, 1)
            sage: Q.reverse().P(GF(3), 3).dimension_vector()
            (4, 1, 1)

        As lists start indexing at 0 the ith vertex corresponds to the (i-1)th entry of
        the dimension vector::

            sage: len(basis_dict[2]) == M.dimension_vector()[1]
            True
        """

        from sage.quivers.representation import QuiverRep
        from sage.quivers.morphism import QuiverRepHom
        if not self._codomain.is_left_module():
            raise ValueError("The codomain must be a left module.")

        # Create the spaces
        spaces = {}
        for v in self._quiver:
            im_gens = [self.hom([self._codomain.left_edge_action((v, v), f(x))
                for x in self._domain.gens()])._vector
                for f in self.gens()]
            spaces[v] = self._space.submodule(im_gens)

        # Create the maps
        maps = {}
        for e in self._quiver.edges():
            e_op = (e[1], e[0], e[2])
            maps[e_op] = []
            for vec in spaces[e[1]].gens():
                vec_im = spaces[e_op[1]].coordinate_vector(self.hom([self._codomain.left_edge_action(e, self.hom(vec)(x))
                                                                     for x in self._domain.gens()])._vector)
                maps[e_op].append(vec_im)

        # Create and return the module (and the dict if desired)
        if basis:
            basis_dict = {}
            for v in self._quiver:
                basis_dict[v] = [QuiverRepHom(self._domain, self._codomain, vec) for vec in spaces[v].gens()]
            return (QuiverRep(self._base, self._quiver.reverse(), spaces, maps), basis_dict)
        else:
            return QuiverRep(self._base, self._quiver.reverse(), spaces, maps)

